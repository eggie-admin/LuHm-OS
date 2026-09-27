package art.eggiebagelface.luhmos.kaiwebview

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import android.webkit.MimeTypeMap
import org.json.JSONArray
import org.json.JSONObject
import org.w3c.dom.Element
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import java.util.zip.ZipFile
import javax.xml.parsers.DocumentBuilderFactory

/**
 * App-private, content-addressed proof vault for LuHm WebGlass.
 *
 * Raw SAF URIs and absolute filesystem paths never enter proof packets. Imported bytes
 * are copied into a dedicated internal directory, SHA-256 pinned, then exposed to the
 * local WebView only through WebViewAssetLoader.InternalStoragePathHandler.
 */
class ProofVault(private val context: Context) {
    companion object {
        const val ORIGIN = "https://appassets.androidplatform.net"
        const val WEB_PATH = "/proof-vault/"
        private const val MAX_PROOF_BYTES = 256L * 1024L * 1024L
        private const val MAX_INLINE_TEXT_BYTES = 1024L * 1024L
        private const val MAX_DOCX_BLOCKS = 500
        private val SAFE_EXTENSION = Regex("^[a-z0-9]{1,10}$")
    }

    val rootDir = File(context.filesDir, "luhm-proof-vault").apply { mkdirs() }
    val publicDir = File(rootDir, "public").apply { mkdirs() }
    private val metaDir = File(rootDir, "meta").apply { mkdirs() }

    fun importUri(uri: Uri, persistedPermission: Boolean): JSONObject {
        val resolver = context.contentResolver
        val displayName = queryDisplayName(uri) ?: "proof"
        val declaredSize = querySize(uri)
        val mimeType = resolver.getType(uri) ?: "application/octet-stream"
        val extension = safeExtension(displayName, mimeType)
        val temp = File.createTempFile("incoming-", ".part", publicDir)
        val digest = MessageDigest.getInstance("SHA-256")
        var bytes = 0L

        try {
            resolver.openInputStream(uri)?.use { input ->
                FileOutputStream(temp).use { output ->
                    val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                    while (true) {
                        val count = input.read(buffer)
                        if (count < 0) break
                        bytes += count
                        if (bytes > MAX_PROOF_BYTES) {
                            throw IllegalArgumentException("proof exceeds bounded import size")
                        }
                        digest.update(buffer, 0, count)
                        output.write(buffer, 0, count)
                    }
                    output.fd.sync()
                }
            } ?: throw IllegalArgumentException("unable to open selected proof")

            if (declaredSize != null && declaredSize >= 0L && declaredSize != bytes) {
                throw IllegalArgumentException("selected proof size changed during import")
            }

            val sha256 = digest.digest().joinToString("") { "%02x".format(it) }
            val fileName = if (extension.isBlank()) sha256 else "$sha256.$extension"
            val finalFile = File(publicDir, fileName)
            if (finalFile.exists()) {
                temp.delete()
            } else if (!temp.renameTo(finalFile)) {
                throw IllegalStateException("unable to seal proof into vault")
            }

            val type = viewerType(mimeType, extension)
            val localUrl = "$ORIGIN$WEB_PATH$fileName"
            val packet = JSONObject()
                .put("schema", "luhm.proof.vault.v1")
                .put("id", sha256)
                .put("status", "UNKNOWN")
                .put("type", type)
                .put("title", displayName.take(180))
                .put("mime", mimeType)
                .put("sha256", sha256)
                .put("provenance", "android-saf-local-copy")
                .put("capturedAt", System.currentTimeMillis().toString())
                .put("sourceRef", "ANDROID_LOCAL_VAULT")
                .put("greenAuthority", false)
                .put("fields", JSONObject()
                    .put("mimeType", mimeType)
                    .put("size", bytes)
                    .put("sourceKind", "android-saf")
                    .put("persistedPermission", persistedPermission)
                    .put("importState", "IMPORTED_NOT_ADJUDICATED"))

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
            throw error
        }
    }

    fun listPackets(): JSONArray {
        val out = JSONArray()
        metaDir.listFiles { file -> file.isFile && file.extension == "json" }
            ?.sortedByDescending { it.lastModified() }
            ?.forEach { file ->
                runCatching { JSONObject(file.readText(Charsets.UTF_8)) }
                    .getOrNull()
                    ?.let(out::put)
            }
        return out
    }

    fun packet(proofId: String): JSONObject? {
        if (!proofId.matches(Regex("^[a-f0-9]{64}$"))) return null
        val file = File(metaDir, "$proofId.json")
        if (!file.isFile) return null
        return runCatching { JSONObject(file.readText(Charsets.UTF_8)) }.getOrNull()
    }

    private fun writeMeta(sha256: String, packet: JSONObject) {
        val temp = File(metaDir, "$sha256.json.tmp")
        val sealed = File(metaDir, "$sha256.json")
        temp.writeText(packet.toString(2) + "\n", Charsets.UTF_8)
        if (sealed.exists()) sealed.delete()
        if (!temp.renameTo(sealed)) {
            temp.delete()
            throw IllegalStateException("unable to seal proof metadata")
        }
    }

    private fun readBoundedText(file: File): String {
        if (file.length() > MAX_INLINE_TEXT_BYTES) return "Text proof retained in vault; inline preview exceeds 1 MiB bound."
        return file.readText(Charsets.UTF_8).take(200000)
    }

    private fun readJson(file: File): Any {
        if (file.length() > MAX_INLINE_TEXT_BYTES) return JSONObject().put("preview", "JSON retained in vault; inline preview exceeds 1 MiB bound.")
        val text = file.readText(Charsets.UTF_8)
        return runCatching { JSONObject(text) }.getOrElse {
            runCatching { JSONArray(text) }.getOrElse {
                JSONObject().put("parseError", "Selected JSON could not be parsed safely.")
            }
        }
    }

    private fun extractDocxBlocks(file: File): JSONArray {
        val blocks = JSONArray()
        runCatching {
            ZipFile(file).use { zip ->
                val entry = zip.getEntry("word/document.xml") ?: return@use
                val factory = DocumentBuilderFactory.newInstance().apply {
                    isNamespaceAware = true
                    isExpandEntityReferences = false
                    runCatching { setFeature("http://apache.org/xml/features/disallow-doctype-decl", true) }
                    runCatching { setFeature("http://xml.org/sax/features/external-general-entities", false) }
                    runCatching { setFeature("http://xml.org/sax/features/external-parameter-entities", false) }
                    runCatching { setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false) }
                }
                val document = zip.getInputStream(entry).use { factory.newDocumentBuilder().parse(it) }
                val paragraphs = document.getElementsByTagNameNS("*", "p")
                for (index in 0 until paragraphs.length) {
                    if (blocks.length() >= MAX_DOCX_BLOCKS) break
                    val paragraph = paragraphs.item(index) as? Element ?: continue
                    val textNodes = paragraph.getElementsByTagNameNS("*", "t")
                    val text = buildString {
                        for (textIndex in 0 until textNodes.length) append(textNodes.item(textIndex).textContent)
                    }.trim()
                    if (text.isEmpty()) continue
                    val styles = paragraph.getElementsByTagNameNS("*", "pStyle")
                    val style = if (styles.length > 0) {
                        val node = styles.item(0) as? Element
                        node?.getAttributeNS("http://schemas.openxmlformats.org/wordprocessingml/2006/main", "val")
                            ?.ifBlank { node.getAttribute("w:val") }
                            .orEmpty()
                    } else ""
                    val headingLevel = Regex("(?i)heading\\s*([1-3])").find(style)?.groupValues?.getOrNull(1)?.toIntOrNull()
                    val block = if (headingLevel != null) {
                        JSONObject().put("type", "heading").put("level", headingLevel).put("text", text.take(20000))
                    } else {
                        JSONObject().put("type", "paragraph").put("text", text.take(20000))
                    }
                    blocks.put(block)
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
