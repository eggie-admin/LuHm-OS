package art.eggiebagelface.luhmos.kaiwebview

import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.view.Gravity
import android.view.View
import android.view.ViewGroup
import android.view.WindowInsets
import android.view.WindowInsetsController
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.FrameLayout
import androidx.webkit.JavaScriptReplyProxy
import androidx.webkit.WebMessageCompat
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import org.godotengine.godot.Godot
import org.godotengine.godot.plugin.GodotPlugin
import org.godotengine.godot.plugin.SignalInfo
import org.godotengine.godot.plugin.UsedByGodot
import org.json.JSONObject

class KAIWebView(godot: Godot) : GodotPlugin(godot) {
    companion object {
        private const val ORIGIN = "https://appassets.androidplatform.net"
        private const val START_URL = "$ORIGIN/assets/cockpit/index.html"
        private val BRIDGE_SIGNAL = SignalInfo("bridge_message", String::class.java)
        private val SAFE_MODES = setOf("full", "mini", "pet", "bubble")
    }

    private var webView: WebView? = null
    private var currentMode = "full"

    override fun getPluginName() = BuildConfig.GODOT_PLUGIN_NAME

    override fun getPluginSignals() = setOf(BRIDGE_SIGNAL)

    @UsedByGodot
    fun showCockpit() {
        runOnHostThread {
            enterImmersiveCage()
            val view = ensureWebView()
            applyCockpitMode(view, currentMode)
            view.visibility = View.VISIBLE
        }
    }

    @UsedByGodot
    fun hideCockpit() {
        runOnHostThread {
            webView?.visibility = View.GONE
        }
    }

    @UsedByGodot
    fun setCockpitMode(mode: String): Boolean {
        if (mode !in SAFE_MODES) return false
        currentMode = mode
        runOnHostThread {
            enterImmersiveCage()
            val view = ensureWebView()
            applyCockpitMode(view, mode)
            view.visibility = View.VISIBLE
        }
        return true
    }

    @UsedByGodot
    fun backgroundTask(): Boolean {
        val host = activity ?: return false
        runOnHostThread {
            // This is ordinary Android task backgrounding, not a persistent service.
            host.moveTaskToBack(true)
        }
        return true
    }

    @UsedByGodot
    fun finishTask(): Boolean {
        val host = activity ?: return false
        runOnHostThread {
            // Explicit human-requested exit. No killProcess/System.exit shortcut.
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                host.finishAndRemoveTask()
            } else {
                host.finish()
            }
        }
        return true
    }

    @UsedByGodot
    fun isCockpitReady(): Boolean = webView != null

    @UsedByGodot
    fun getSystemProfile(): String {
        val host = activity ?: return JSONObject()
            .put("schema", "luhm.samsung.system-profile.v1")
            .put("available", false)
            .toString()
        return SamsungSystemProfile.snapshot(host).toString()
    }

    @UsedByGodot
    fun getShizukuCapability(): String = ShizukuCapability.snapshot().toString()

    @UsedByGodot
    fun requestShizukuPermissionFromNativeUserAction(): Boolean =
        ShizukuCapability.requestPermissionFromExplicitNativeAction()

    @UsedByGodot
    fun postToCockpit(json: String) {
        runOnHostThread {
            val quoted = JSONObject.quote(json)
            webView?.evaluateJavascript(
                "window.dispatchEvent(new MessageEvent('message',{data:$quoted}));",
                null
            )
        }
    }

    private fun ensureWebView(): WebView {
        webView?.let { return it }
        val host = activity ?: error("KAIWebView host activity unavailable")
        val loader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(host))
            .build()

        val view = WebView(host)
        view.setBackgroundColor(Color.TRANSPARENT)
        view.overScrollMode = View.OVER_SCROLL_NEVER
        view.isHapticFeedbackEnabled = false
        view.setOnLongClickListener { true }
        view.settings.apply {
            javaScriptEnabled = true
            javaScriptCanOpenWindowsAutomatically = false
            domStorageEnabled = false
            databaseEnabled = false
            allowFileAccess = false
            allowContentAccess = false
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            cacheMode = WebSettings.LOAD_NO_CACHE
            setSupportMultipleWindows(false)
            setSupportZoom(false)
            builtInZoomControls = false
            displayZoomControls = false
            mediaPlaybackRequiresUserGesture = true
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                safeBrowsingEnabled = true
            }
        }

        view.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView?,
                request: WebResourceRequest?
            ): WebResourceResponse? = request?.url?.let(loader::shouldInterceptRequest)

            override fun shouldOverrideUrlLoading(
                view: WebView?,
                request: WebResourceRequest?
            ): Boolean {
                val uri = request?.url ?: return true
                return uri.scheme != "https" || uri.host != "appassets.androidplatform.net"
            }
        }

        if (WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            WebViewCompat.addWebMessageListener(
                view,
                "LuHmNative",
                setOf(ORIGIN),
                WebViewCompat.WebMessageListener { _, message, sourceOrigin, isMainFrame, replyProxy ->
                    handleBridgeMessage(message, sourceOrigin, isMainFrame, replyProxy)
                }
            )
        }

        val root = host.findViewById<ViewGroup>(android.R.id.content)
        root.addView(view, fullScreenParams())
        view.loadUrl(START_URL)
        webView = view
        return view
    }

    private fun applyCockpitMode(view: WebView, mode: String) {
        val params = when (mode) {
            "mini" -> FrameLayout.LayoutParams(dp(360), dp(150), Gravity.TOP or Gravity.END).apply {
                topMargin = dp(18)
                marginEnd = dp(12)
            }
            "pet" -> FrameLayout.LayoutParams(dp(300), dp(390), Gravity.END or Gravity.CENTER_VERTICAL).apply {
                marginEnd = dp(12)
            }
            "bubble" -> FrameLayout.LayoutParams(dp(92), dp(92), Gravity.END or Gravity.CENTER_VERTICAL).apply {
                marginEnd = dp(10)
            }
            else -> fullScreenParams()
        }
        view.layoutParams = params
        view.bringToFront()
        val quoted = JSONObject.quote(mode)
        view.evaluateJavascript(
            "document.documentElement.setAttribute('data-shell-mode',$quoted);",
            null
        )
    }

    private fun fullScreenParams() = FrameLayout.LayoutParams(
        ViewGroup.LayoutParams.MATCH_PARENT,
        ViewGroup.LayoutParams.MATCH_PARENT,
        Gravity.FILL
    )

    private fun dp(value: Int): Int {
        val density = activity?.resources?.displayMetrics?.density ?: 1f
        return (value * density).toInt()
    }

    private fun enterImmersiveCage() {
        val host = activity ?: return
        val decor = host.window.decorView
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            host.window.setDecorFitsSystemWindows(false)
            decor.windowInsetsController?.let { controller ->
                controller.hide(WindowInsets.Type.statusBars() or WindowInsets.Type.navigationBars())
                controller.systemBarsBehavior =
                    WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            }
        } else {
            @Suppress("DEPRECATION")
            decor.systemUiVisibility = (
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    or View.SYSTEM_UI_FLAG_FULLSCREEN
                    or View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    or View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    or View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    or View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            )
        }
    }

    private fun handleBridgeMessage(
        message: WebMessageCompat,
        sourceOrigin: Uri,
        isMainFrame: Boolean,
        replyProxy: JavaScriptReplyProxy
    ) {
        if (!isMainFrame || sourceOrigin.toString() != ORIGIN) return
        val raw = message.data ?: return
        val parsed = runCatching { JSONObject(raw) }.getOrNull() ?: return
        if (parsed.optString("schema") != "luhm.bridge.v1") return

        when (parsed.optString("type")) {
            "status.request" -> {
                val host = activity
                val systemProfile = if (host == null) {
                    JSONObject()
                        .put("schema", "luhm.samsung.system-profile.v1")
                        .put("available", false)
                } else {
                    SamsungSystemProfile.snapshot(host)
                }
                replyProxy.postMessage(
                    JSONObject()
                        .put("schema", "luhm.bridge.reply.v1")
                        .put("type", "status")
                        .put(
                            "payload",
                            JSONObject()
                                .put("kai", "native")
                                .put("ollama", "external")
                                .put("system", systemProfile)
                                .put("cockpitMode", currentMode)
                        )
                        .toString()
                )
            }
            "chat.send", "panel.set", "model.select", "cms.select", "ui.mode", "app.background", "app.exit" ->
                emitSignal(BRIDGE_SIGNAL.name, raw)
            else -> Unit
        }
    }
}
