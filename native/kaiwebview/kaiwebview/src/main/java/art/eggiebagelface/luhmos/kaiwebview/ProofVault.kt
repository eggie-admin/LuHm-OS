package art.eggiebagelface.luhmos.kaiwebview

import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import android.webkit.MimeTypeMap
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest

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

            val packet = JSONObject()
                .put("schema", "luhm.proof.vault.v1")
                .put("id", sha256)
                .put("status", "IMPORTED_NOT_ADJUDICATED")
                .put("type", viewerType(mimeType, extension))
                .put("title", displayName.take(180))
                .put("mimeType", mimeType)
                .put("size", bytes)
                .put("sha256", sha256)
                .put("sourceKind", "android-saf")
                .put("persistedPermission", persistedPermission)
                .put("capturedAtEpochMs", System.currentTimeMillis())
                .put("localUrl", "$ORIGIN$WEB_PATH$fileName")
                .put("rawHtmlTrusted", false)
                .put("greenAuthority", false)

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
