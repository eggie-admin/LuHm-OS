package art.eggiebagelface.luhmos.kaiwebview

import android.content.pm.PackageManager
import org.json.JSONObject
import rikka.shizuku.Shizuku

/**
 * Read-only Shizuku capability snapshot for LuHm status/UI surfaces.
 *
 * This class never requests permission, starts a user service, executes shell commands,
 * mutates Android settings, or bypasses Secure Folder. It only reports the binder and
 * already-granted permission state exposed by the official Shizuku API.
 */
object ShizukuCapabilityProbe {
    fun snapshot(): JSONObject {
        val binderAlive = runCatching { Shizuku.pingBinder() }.getOrDefault(false)
        val permission = if (!binderAlive) {
            "UNAVAILABLE"
        } else {
            when (runCatching { Shizuku.checkSelfPermission() }.getOrDefault(PackageManager.PERMISSION_DENIED)) {
                PackageManager.PERMISSION_GRANTED -> "GRANTED"
                else -> "NOT_GRANTED"
            }
        }

        return JSONObject()
            .put("schema", "luhm.android.shizuku-capability.v1")
            .put("mode", "DETECT_ONLY")
            .put("binderAlive", binderAlive)
            .put("permission", permission)
            .put("permissionRequestedByProbe", false)
            .put("genericShell", false)
            .put("secureFolderBypass", false)
            .put("silentInstall", false)
            .put("mutationAuthority", false)
            .put("crownAuthority", false)
    }
}
