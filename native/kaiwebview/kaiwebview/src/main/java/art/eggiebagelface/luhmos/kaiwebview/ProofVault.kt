package art.eggiebagelface.luhmos.kaiwebview

import android.content.Context
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.OpenableColumns
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import android.security.keystore.StrongBoxUnavailableException
import android.webkit.MimeTypeMap
import android.webkit.WebResourceResponse
import org.json.JSONArray
import org.json.JSONObject
import org.w3c.dom.Element
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.io.InputStream
import java.security.KeyStore
import java.security.MessageDigest
import java.util.zip.ZipInputStream
import javax.crypto.Cipher
import javax.crypto.CipherInputStream
import javax.crypto.CipherOutputStream
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import javax.xml.parsers.DocumentBuilderFactory

/**
 * App-private, content-addressed and encrypted proof vault for LuHm WebGlass.
 *
 * Raw SAF URIs and absolute filesystem paths never enter proof packets. Imported bytes
 * are SHA-256 pinned while being encrypted directly to app-private storage with
 * AES-256-GCM. The AES key lives in Android Keystore; StrongBox is requested when the
 * device supports it and Android Keystore remains the fail-safe fallback.
 *
 * Decrypted proof bytes are streamed on demand through a WebViewAssetLoader PathHandler.
 * No decrypted proof copy is written back to disk by this class.
 */
class ProofVault(private val context: Context) {
    companion object {
        const val ORIGIN = "https://appassets.androidplatform.net"
        const val WEB_PATH = "/proof-vault/"
        private const val MAX_PROOF_BYTES = 256L * 1024L * 1024L
        private const val MAX_INLINE_TEXT_BYTES = 1024L * 1024L
        private const val MAX_DOCX_BLOCKS = 500
        private const val KEY_ALIAS = "luhm-proof-vault-aes-gcm-v1"
        private const val GCM_TAG_BITS = 128
        private const val AES_KEY_BITS = 256
        private val SAFE_EXTENSION = Regex("^[a-z0-9]{1,10}$")
        private val WEB_RESOURCE = Regex("^([a-f0-9]{64})(?:\\.([a-z0-9]{1,10}))?$")
        private val MAGIC = "LUHMENC1".toByteArray(Charsets.US_ASCII)
    }

    val rootDir = File(context.filesDir, "luhm-proof-vault").apply { mkdirs() }
    private val encryptedDir = File(rootDir, "encrypted").apply { mkdirs() }
    private val metaDir = File(rootDir, "meta").apply { mkdirs() }

    fun importUri(uri: Uri, persistedPermission: Boolean): JSONObject {
        val resolver = context.contentResolver
        val displayName = queryDisplayName(uri) ?: "proof"
        val declaredSize = querySize(uri)
        val mimeType = resolver.getType(uri) ?: "application/octet-stream"
        val extension = safeExtension(displayName, mimeType)
        val temp = File.createTempFile("incoming-", ".gcm.part", encryptedDir)
        val digest = MessageDigest.getInstance("SHA-256")
        var bytes = 0L
        var createdFinal: File? = null

        try {
            resolver.openInputStream(uri)?.use { input ->
                encryptedOutput(temp).use { encrypted ->
                    val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                    while (true) {
                        val count = input.read(buffer)
                        if (count < 0) break
                        bytes += count
                        if (bytes > MAX_PROOF_BYTES) {
                            throw IllegalArgumentException("proof exceeds bounded import size")
                        }
                        digest.update(buffer, 0, count)
                        encrypted.write(buffer, 0, count)
                    }
                }
            } ?: throw IllegalArgumentException("unable to open selected proof")

            if (declaredSize != null && declaredSize >= 0L && declaredSize != bytes) {
                throw IllegalArgumentException("selected proof size changed during import")
            }

            val sha256 = digest.digest().joinToString("") { "%02x".format(it) }
            val finalFile = encryptedBlob(sha256)
            if (finalFile.exists()) {
                temp.delete()
            } else if (!temp.renameTo(finalFile)) {
                throw IllegalStateException("unable to seal encrypted proof into vault")
            } else {
                createdFinal = finalFile
            }

            val type = viewerType(mimeType, extension)
            val logicalName = if (extension.isBlank()) sha256 else "$sha256.$extension"
            val localUrl = "$ORIGIN$WEB_PATH$logicalName"
            val packet = JSONObject()
                .put("schema", "luhm.proof.vault.v2")
                .put("id", sha256)
                .put("status", "UNKNOWN")
                .put("type", type)
                .put("title", displayName.take(180))
                .put("mime", mimeType)
                .put("sha256", sha256)
                .put("provenance", "android-saf-local-encrypted-copy")
                .put("capturedAt", System.currentTimeMillis().toString())
                .put("sourceRef", "ANDROID_LOCAL_VAULT")
                .put("rawHtmlTrusted", false)
                .put("greenAuthority", false)
                .put("fields", JSONObject()
                    .put("mimeType", mimeType)
                    .put("size", bytes)
                    .put("sourceKind", "android-saf")
                    .put("persistedPermission", persistedPermission)
                    .put("importState", "IMPORTED_ENCRYPTED_NOT_ADJUDICATED")
                    .put("storageEncryption", "AES-256-GCM")
                    .put("keyStore", "AndroidKeyStore")
                    .put("plaintextAtRest", false))

            when (type) {
                "pdf", "image", "asset" -> packet.put("url", localUrl)
                "docx" -> packet.put("blocks", extractDocxBlocks(finalFile))
                "json" -> packet.put("data", readJson(finalFile))
                "text" -> packet.put("text", readBoundedText(finalFile))
            }

            writeMeta(sha256, packet)
            return packet
        } catch (error: Exception) {
            temp.delete()
            createdFinal?.delete()
            throw error
        }
    }

    fun listPackets(): JSONArray {
        val out = JSONArray()
        metaDir.listFiles { file -> file.isFile && file.name.endsWith(".json.gcm") }
            ?.sortedByDescending { it.lastModified() }
            ?.forEach { file ->
                runCatching { JSONObject(readEncryptedText(file, MAX_INLINE_TEXT_BYTES)) }
                    .getOrNull()
                    ?.let(out::put)
            }
        return out
    }

    fun packet(proofId: String): JSONObject? {
        if (!proofId.matches(Regex("^[a-f0-9]{64}$"))) return null
        val file = encryptedMeta(proofId)
        if (!file.isFile) return null
        return runCatching { JSONObject(readEncryptedText(file, MAX_INLINE_TEXT_BYTES)) }.getOrNull()
    }

    fun openWebResource(path: String): WebResourceResponse? {
        val match = WEB_RESOURCE.matchEntire(path.substringBefore('?').substringBefore('#')) ?: return null
        val proofId = match.groupValues[1]
        val packet = packet(proofId) ?: return null
        val blob = encryptedBlob(proofId)
        if (!blob.isFile) return null
        val mime = packet.optString("mime", "application/octet-stream")
        return runCatching {
            WebResourceResponse(mime, null, decryptedInput(blob))
        }.getOrNull()
    }

    private fun encryptedBlob(sha256: String) = File(encryptedDir, "$sha256.blob.gcm")
    private fun encryptedMeta(sha256: String) = File(metaDir, "$sha256.json.gcm")

    private fun writeMeta(sha256: String, packet: JSONObject) {
        val temp = File(metaDir, "$sha256.json.gcm.tmp")
        val sealed = encryptedMeta(sha256)
        encryptedOutput(temp).use { output ->
            output.write((packet.toString(2) + "\n").toByteArray(Charsets.UTF_8))
        }
        if (sealed.exists() && !sealed.delete()) {
            temp.delete()
            throw IllegalStateException("unable to replace encrypted proof metadata")
        }
        if (!temp.renameTo(sealed)) {
            temp.delete()
            throw IllegalStateException("unable to seal encrypted proof metadata")
        }
    }

    private fun vaultKey(): SecretKey {
        val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
        (keyStore.getKey(KEY_ALIAS, null) as? SecretKey)?.let { return it }

        fun generate(useStrongBox: Boolean): SecretKey {
            val builder = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(AES_KEY_BITS)
                .setRandomizedEncryptionRequired(true)
                .setUserAuthenticationRequired(false)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P && useStrongBox) {
                builder.setIsStrongBoxBacked(true)
            }
            return KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore").run {
                init(builder.build())
                generateKey()
            }
        }

        val strongBoxAvailable = Build.VERSION.SDK_INT >= Build.VERSION_CODES.P &&
            context.packageManager.hasSystemFeature(PackageManager.FEATURE_STRONGBOX_KEYSTORE)
        return if (strongBoxAvailable) {
            try {
                generate(true)
            } catch (_: StrongBoxUnavailableException) {
                generate(false)
            }
        } else {
            generate(false)
        }
    }

    private fun encryptedOutput(file: File): CipherOutputStream {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.ENCRYPT_MODE, vaultKey())
        val iv = cipher.iv
        require(iv.isNotEmpty() && iv.size <= 255) { "invalid AES-GCM IV" }
        val raw = FileOutputStream(file)
        raw.write(MAGIC)
        raw.write(iv.size)
        raw.write(iv)
        return CipherOutputStream(raw, cipher)
    }

    private fun decryptedInput(file: File): InputStream {
        val raw = FileInputStream(file)
        try {
            val magic = ByteArray(MAGIC.size)
            if (raw.read(magic) != MAGIC.size || !magic.contentEquals(MAGIC)) {
                throw IllegalArgumentException("encrypted proof header mismatch")
            }
            val ivSize = raw.read()
            if (ivSize !in 12..32) throw IllegalArgumentException("encrypted proof IV invalid")
            val iv = ByteArray(ivSize)
            if (raw.read(iv) != ivSize) throw IllegalArgumentException("encrypted proof IV truncated")
            val cipher = Cipher.getInstance("AES/GCM/NoPadding")
            cipher.init(Cipher.DECRYPT_MODE, vaultKey(), GCMParameterSpec(GCM_TAG_BITS, iv))
            return CipherInputStream(raw, cipher)
        } catch (error: Exception) {
            raw.close()
            throw error
        }
    }

    private fun readEncryptedText(file: File, maxBytes: Long): String {
        decryptedInput(file).use { input ->
            val out = ByteArrayOutputStream()
            val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
            var total = 0L
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                total += count
                if (total > maxBytes) throw IllegalArgumentException("encrypted text exceeds preview bound")
                out.write(buffer, 0, count)
            }
            return out.toString(Charsets.UTF_8.name())
        }
    }

    private fun readBoundedText(file: File): String = runCatching {
        readEncryptedText(file, MAX_INLINE_TEXT_BYTES).take(200000)
    }.getOrElse {
        "Text proof retained encrypted in vault; inline preview exceeds 1 MiB bound or could not be decrypted."
    }

    private fun readJson(file: File): Any {
        val value = runCatching { readEncryptedText(file, MAX_INLINE_TEXT_BYTES) }.getOrElse {
            return JSONObject().put("preview", "JSON retained encrypted in vault; inline preview exceeds 1 MiB bound or could not be decrypted.")
        }
        return runCatching { JSONObject(value) }.getOrElse {
            runCatching { JSONArray(value) }.getOrElse {
                JSONObject().put("parseError", "Selected JSON could not be parsed safely.")
            }
        }
    }

    private fun extractDocxBlocks(file: File): JSONArray {
        val blocks = JSONArray()
        runCatching {
            decryptedInput(file).use { decrypted ->
                ZipInputStream(decrypted).use { zip ->
                    while (true) {
                        val entry = zip.nextEntry ?: break
                        if (entry.name != "word/document.xml") continue
                        val xml = ByteArrayOutputStream()
                        val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                        while (true) {
                            val count = zip.read(buffer)
                            if (count < 0) break
                            if (xml.size().toLong() + count > MAX_INLINE_TEXT_BYTES * 8) {
                                throw IllegalArgumentException("DOCX document.xml exceeds parse bound")
                            }
                            xml.write(buffer, 0, count)
                        }
                        val factory = DocumentBuilderFactory.newInstance().apply {
                            isNamespaceAware = true
                            isExpandEntityReferences = false
                            runCatching { setFeature("http://apache.org/xml/features/disallow-doctype-decl", true) }
                            runCatching { setFeature("http://xml.org/sax/features/external-general-entities", false) }
                            runCatching { setFeature("http://xml.org/sax/features/external-parameter-entities", false) }
                            runCatching { setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false) }
                        }
                        val document = factory.newDocumentBuilder().parse(ByteArrayInputStream(xml.toByteArray()))
                        val paragraphs = document.getElementsByTagNameNS("*", "p")
                        for (index in 0 until paragraphs.length) {
                            if (blocks.length() >= MAX_DOCX_BLOCKS) break
                            val paragraph = paragraphs.item(index) as? Element ?: continue
                            val textNodes = paragraph.getElementsByTagNameNS("*", "t")
                            val paragraphText = buildString {
                                for (textIndex in 0 until textNodes.length) append(textNodes.item(textIndex).textContent)
                            }.trim()
                            if (paragraphText.isEmpty()) continue
                            val styles = paragraph.getElementsByTagNameNS("*", "pStyle")
                            val styleNode = if (styles.length > 0) styles.item(0) as? Element else null
                            val namespaceStyle = styleNode
                                ?.getAttributeNS("http://schemas.openxmlformats.org/wordprocessingml/2006/main", "val")
                                .orEmpty()
                            val style = if (namespaceStyle.isNotBlank()) namespaceStyle else styleNode?.getAttribute("w:val").orEmpty()
                            val headingLevel = Regex("(?i)heading\\s*([1-3])")
                                .find(style)?.groupValues?.getOrNull(1)?.toIntOrNull()
                            val block = if (headingLevel != null) {
                                JSONObject().put("type", "heading").put("level", headingLevel).put("text", paragraphText.take(20000))
                            } else {
                                JSONObject().put("type", "paragraph").put("text", paragraphText.take(20000))
                            }
                            blocks.put(block)
                        }
                        break
                    }
                }
            }
        }
        return blocks
    }

    private fun queryDisplayName(uri: Uri): String? = context.contentResolver
        .query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)
        ?.use { cursor ->
            if (!cursor.moveToFirst()) null else {
                val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (index < 0) null else cursor.getString(index)
            }
        }

    private fun querySize(uri: Uri): Long? = context.contentResolver
        .query(uri, arrayOf(OpenableColumns.SIZE), null, null, null)
        ?.use { cursor ->
            if (!cursor.moveToFirst()) null else {
                val index = cursor.getColumnIndex(OpenableColumns.SIZE)
                if (index < 0 || cursor.isNull(index)) null else cursor.getLong(index)
            }
        }

    private fun safeExtension(displayName: String, mimeType: String): String {
        val fromName = displayName.substringAfterLast('.', "").lowercase()
        if (SAFE_EXTENSION.matches(fromName)) return fromName
        val fromMime = MimeTypeMap.getSingleton().getExtensionFromMimeType(mimeType)?.lowercase().orEmpty()
        return if (SAFE_EXTENSION.matches(fromMime)) fromMime else ""
    }

    private fun viewerType(mimeType: String, extension: String): String = when {
        mimeType == "application/pdf" || extension == "pdf" -> "pdf"
        mimeType == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" || extension == "docx" -> "docx"
        mimeType.startsWith("image/") -> "image"
        mimeType == "application/json" || extension == "json" -> "json"
        mimeType.startsWith("text/") -> "text"
        else -> "asset"
    }
}
