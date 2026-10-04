package art.eggiebagelface.luhmos.kaiwebview

import android.app.admin.DevicePolicyManager
import android.content.Context
import android.os.Build
import android.os.UserManager
import android.webkit.WebView
import org.json.JSONObject

internal object SamsungSystemProfile {
    private val trackedPackages = listOf(
        "com.android.chrome",
        "com.chrome.beta",
        "com.chrome.dev",
        "com.chrome.canary",
        "com.google.android.webview",
        "com.google.android.webview.beta",
        "com.google.android.webview.dev",
        "com.google.android.webview.canary"
    )

    @Suppress("DEPRECATION")
    fun snapshot(context: Context): JSONObject {
        val packageManager = context.packageManager
        val devicePolicy = context.getSystemService(DevicePolicyManager::class.java)
        val userManager = context.getSystemService(UserManager::class.java)
        val currentWebView = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            WebView.getCurrentWebViewPackage()
        } else {
            null
        }

        val packages = JSONObject()
        trackedPackages.forEach { packageName ->
            val info = runCatching { packageManager.getPackageInfo(packageName, 0) }.getOrNull()
            if (info == null) {
                packages.put(packageName, JSONObject.NULL)
            } else {
                val enabled = runCatching {
                    packageManager.getApplicationInfo(packageName, 0).enabled
                }.getOrDefault(false)
                packages.put(
                    packageName,
                    JSONObject()
                        .put("versionName", info.versionName ?: "unknown")
                        .put("enabled", enabled)
                )
            }
        }

        val deviceOwner = devicePolicy?.isDeviceOwnerApp(context.packageName) ?: false
        val profileOwner = devicePolicy?.isProfileOwnerApp(context.packageName) ?: false
        val managedProfile = userManager?.isManagedProfile ?: false
        val adminMode = when {
            deviceOwner -> "device_owner"
            profileOwner -> "profile_owner"
            managedProfile -> "managed_profile_member"
            else -> "standard_app"
        }

        return JSONObject()
            .put("schema", "luhm.samsung.system-profile.v1")
            .put("manufacturer", Build.MANUFACTURER)
            .put("brand", Build.BRAND)
            .put("model", Build.MODEL)
            .put("sdk", Build.VERSION.SDK_INT)
            .put("androidRelease", Build.VERSION.RELEASE)
            .put("adminMode", adminMode)
            .put("managedProfile", managedProfile)
            .put("deviceOwner", deviceOwner)
            .put("profileOwner", profileOwner)
            .put("rootBridgeEnabled", false)
            .put("termuxAdminLoginSupported", false)
            .put(
                "webViewProvider",
                if (currentWebView == null) {
                    JSONObject.NULL
                } else {
                    JSONObject()
                        .put("packageName", currentWebView.packageName)
                        .put("versionName", currentWebView.versionName ?: "unknown")
                }
            )
            .put("packages", packages)
    }
}
