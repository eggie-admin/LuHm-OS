package art.eggiebagelface.luhmos.kaiwebview

import android.content.pm.PackageManager
import org.json.JSONObject
import rikka.shizuku.Shizuku

internal object ShizukuCapability {
    const val REQUEST_CODE = 9001

    fun snapshot(): JSONObject {
        val binderAlive = runCatching { Shizuku.pingBinder() }.getOrDefault(false)
        val permission = if (!binderAlive) {
            "unavailable"
        } else {
            runCatching {
                when {
                    Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED -> "granted"
                    Shizuku.shouldShowRequestPermissionRationale() -> "denied_rationale"
                    else -> "not_granted"
                }
            }.getOrDefault("unknown")
        }

        val uid = if (binderAlive) runCatching { Shizuku.getUid() }.getOrNull() else null
        val identity = when (uid) {
            0 -> "root_lab"
            2000 -> "adb_shell"
            null -> "none"
            else -> "uid_$uid"
        }

        return JSONObject()
            .put("schema", "luhm.shizuku.capability.v1")
            .put("binderAlive", binderAlive)
            .put("permission", permission)
            .put("identity", identity)
            .put("uid", uid ?: JSONObject.NULL)
            .put("genericShellEnabled", false)
            .put("userServiceEnabled", false)
            .put("crossProfileBypassEnabled", false)
            .put("webViewPrivilegeBridgeEnabled", false)
            .put("autoPermissionRequest", false)
    }

    fun requestPermissionFromExplicitNativeAction(): Boolean {
        if (!runCatching { Shizuku.pingBinder() }.getOrDefault(false)) return false
        if (runCatching { Shizuku.checkSelfPermission() }.getOrDefault(PackageManager.PERMISSION_DENIED)
            == PackageManager.PERMISSION_GRANTED) return false
        if (runCatching { Shizuku.shouldShowRequestPermissionRationale() }.getOrDefault(false)) return false
        return runCatching {
            Shizuku.requestPermission(REQUEST_CODE)
            true
        }.getOrDefault(false)
    }
}
