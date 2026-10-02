package art.eggiebagelface.luhmos.web3

import android.app.Activity
import android.net.Uri
import android.view.View
import android.view.ViewGroup
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.widget.FrameLayout
import androidx.webkit.WebMessageCompat
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewClientCompat
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import org.godotengine.godot.Godot
import org.godotengine.godot.plugin.GodotPlugin
import org.godotengine.godot.plugin.SignalInfo
import org.godotengine.godot.plugin.UsedByGodot
import org.json.JSONObject
import java.io.ByteArrayInputStream

class AndroidWeb3CockpitPlugin(godot: Godot) : GodotPlugin(godot) {
    companion object {
        private const val LOCAL_ORIGIN = "https://appassets.androidplatform.net"
        private const val LOCAL_PREFIX = "/assets/"
        private const val START_URL = "$LOCAL_ORIGIN$LOCAL_PREFIX" + "index.html"
        private const val BRIDGE_OBJECT = "LuHmNative"

        private val WORLD_REQUESTED = SignalInfo("world_requested")
        private val COCKPIT_READY = SignalInfo("cockpit_ready", String::class.java)
        private val BRIDGE_ERROR = SignalInfo("bridge_error", String::class.java)
    }

    private var cockpitView: WebView? = null
    private var cockpitContainer: FrameLayout? = null

    override fun getPluginName() = BuildConfig.GODOT_PLUGIN_NAME

    override fun getPluginSignals() = setOf(
        WORLD_REQUESTED,
        COCKPIT_READY,
        BRIDGE_ERROR,
    )

    override fun onMainCreate(activity: Activity?): View? {
        val hostActivity = activity ?: return super.onMainCreate(activity)
        val container = FrameLayout(hostActivity)
        val webView = WebView(hostActivity)

        container.layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT,
        )
        webView.layoutParams = FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT,
        )

        configureWebView(hostActivity, webView)
        container.addView(webView)

        cockpitView = webView
        cockpitContainer = container
        webView.loadUrl(START_URL)

        return container
    }

    override fun onMainDestroy() {
        cockpitView?.let { view ->
            view.stopLoading()
            view.loadUrl("about:blank")
            view.removeAllViews()
            view.destroy()
        }
        cockpitView = null
        cockpitContainer = null
        super.onMainDestroy()
    }

    private fun configureWebView(activity: Activity, webView: WebView) {
        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler(
                LOCAL_PREFIX,
                WebViewAssetLoader.AssetsPathHandler(activity),
            )
            .build()

        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = false
            databaseEnabled = false
            allowFileAccess = false
            allowContentAccess = false
            javaScriptCanOpenWindowsAutomatically = false
            setSupportMultipleWindows(false)
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            cacheMode = WebSettings.LOAD_NO_CACHE
            mediaPlaybackRequiresUserGesture = true
        }

        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)

        webView.webViewClient = object : WebViewClientCompat() {
            override fun shouldOverrideUrlLoading(
                view: WebView,
                request: WebResourceRequest,
            ): Boolean {
                val allowed = isAllowedLocalUrl(request.url)
                if (!allowed) {
                    emitSignal(BRIDGE_ERROR.name, "navigation_blocked")
                }
                return !allowed
            }

            override fun shouldInterceptRequest(
                view: WebView,
                request: WebResourceRequest,
            ): WebResourceResponse {
                if (!isAllowedLocalUrl(request.url)) {
                    return blockedResponse()
                }
                return assetLoader.shouldInterceptRequest(request.url) ?: blockedResponse()
            }

            override fun onRenderProcessGone(
                view: WebView,
                detail: RenderProcessGoneDetail,
            ): Boolean {
                emitSignal(
                    BRIDGE_ERROR.name,
                    if (detail.didCrash()) "renderer_crashed" else "renderer_killed",
                )
                cockpitContainer?.removeView(view)
                cockpitView = null
                return true
            }
        }

        if (!WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            emitSignal(BRIDGE_ERROR.name, "web_message_listener_unsupported")
            return
        }

        WebViewCompat.addWebMessageListener(
            webView,
            BRIDGE_OBJECT,
            setOf(LOCAL_ORIGIN),
        ) { _, message: WebMessageCompat, sourceOrigin: Uri, isMainFrame: Boolean, _ ->
            if (!isMainFrame || sourceOrigin.toString() != LOCAL_ORIGIN) {
                emitSignal(BRIDGE_ERROR.name, "bridge_origin_rejected")
                return@addWebMessageListener
            }
            handleBridgeMessage(message.data)
        }
    }

    private fun handleBridgeMessage(raw: String) {
        try {
            when (JSONObject(raw).optString("type")) {
                "world_requested" -> {
                    hideCockpitInternal()
                    emitSignal(WORLD_REQUESTED.name)
                }
                "cockpit_ready" -> {
                    emitSignal(COCKPIT_READY.name, getWebViewVersion())
                }
                else -> emitSignal(BRIDGE_ERROR.name, "bridge_type_rejected")
            }
        } catch (_: Exception) {
            emitSignal(BRIDGE_ERROR.name, "bridge_payload_invalid")
        }
    }

    private fun isAllowedLocalUrl(uri: Uri): Boolean =
        uri.scheme == "https" &&
            uri.host == "appassets.androidplatform.net" &&
            (uri.path ?: "").startsWith(LOCAL_PREFIX)

    private fun blockedResponse(): WebResourceResponse =
        WebResourceResponse(
            "text/plain",
            "utf-8",
            403,
            "Blocked",
            mapOf("Cache-Control" to "no-store"),
            ByteArrayInputStream("blocked".toByteArray(Charsets.UTF_8)),
        )

    private fun hideCockpitInternal() {
        cockpitView?.visibility = View.GONE
    }

    @UsedByGodot
    fun showCockpit() {
        runOnHostThread {
            cockpitView?.apply {
                visibility = View.VISIBLE
                requestFocus()
            }
        }
    }

    @UsedByGodot
    fun hideCockpit() {
        runOnHostThread {
            hideCockpitInternal()
        }
    }

    @UsedByGodot
    fun getWebViewVersion(): String {
        val context = activity ?: return "unavailable"
        val info = WebViewCompat.getCurrentWebViewPackage(context) ?: return "unavailable"
        return "${info.packageName}:${info.versionName ?: "unknown"}"
    }
}
