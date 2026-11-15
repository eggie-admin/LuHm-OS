package art.eggiebagelface.luhmos.web3

import android.app.Activity
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
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
import java.io.ByteArrayOutputStream
import java.io.ByteArrayInputStream

class AndroidWeb3CockpitPlugin(godot: Godot) : GodotPlugin(godot) {
    companion object {
        private const val LOCAL_ORIGIN = "https://appassets.androidplatform.net"
        private const val LOCAL_PREFIX = "/assets/"
        private const val START_URL = "$LOCAL_ORIGIN$LOCAL_PREFIX" + "index.html"
        private const val BRIDGE_OBJECT = "LuHmNative"
        private const val MAX_BRIDGE_MESSAGE_CHARS = 512
        private const val LOCAL_ART_PICK_REQUEST = 7417
        private const val MAX_ART_BYTES = 16L * 1024 * 1024
        private const val MAX_ART_PICKS = 8
        private const val MAX_PREVIEW_EDGE = 1600

        private val WORLD_REQUESTED = SignalInfo("world_requested")
        private val ARAMOOR_REQUESTED = SignalInfo("aramoor_requested")
        private val ONI_REQUESTED = SignalInfo("oni_requested", String::class.java)
        private val COCKPIT_READY = SignalInfo("cockpit_ready", String::class.java)
        private val BRIDGE_ERROR = SignalInfo("bridge_error", String::class.java)

        private val CANONICAL_ONI = setOf(
            "Lum", "Kiri", "Tetsu", "Kaji", "Momo", "Shiori", "DrNao", "Kugi",
            "Fumi", "Sumi", "Koe", "Yume", "Urd", "Belldandy", "Skuld",
        )
    }

    private var cockpitView: WebView? = null
    private var cockpitContainer: FrameLayout? = null
    private var galleryPickerPending = false

    override fun getPluginName() = BuildConfig.GODOT_PLUGIN_NAME

    override fun getPluginSignals() = setOf(
        WORLD_REQUESTED,
        ARAMOOR_REQUESTED,
        ONI_REQUESTED,
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
        galleryPickerPending = false
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
            val raw = message.data
            if (raw == null) {
                emitSignal(BRIDGE_ERROR.name, "bridge_payload_missing")
                return@addWebMessageListener
            }
            handleBridgeMessage(raw)
        }
    }

    private fun handleBridgeMessage(raw: String) {
        if (raw.length > MAX_BRIDGE_MESSAGE_CHARS) {
            emitSignal(BRIDGE_ERROR.name, "bridge_payload_too_large")
            return
        }
        try {
            val payload = JSONObject(raw)
            val expectedKeys = when (payload.optString("type")) {
                "oni_requested" -> setOf("type", "name")
                "world_requested", "aramoor_requested", "cockpit_ready", "local_art_pick_requested" -> setOf("type")
                else -> {
                    emitSignal(BRIDGE_ERROR.name, "bridge_type_rejected")
                    return
                }
            }
            if (payload.keys().asSequence().toSet() != expectedKeys) {
                emitSignal(BRIDGE_ERROR.name, "bridge_keys_rejected")
                return
            }
            when (payload.optString("type")) {
                "world_requested" -> {
                    hideCockpitInternal()
                    emitSignal(WORLD_REQUESTED.name)
                }
                "aramoor_requested" -> {
                    hideCockpitInternal()
                    emitSignal(ARAMOOR_REQUESTED.name)
                }
                "local_art_pick_requested" -> {
                    openLocalArtPicker()
                }
                "oni_requested" -> {
                    val name = payload.optString("name").trim()
                    if (name !in CANONICAL_ONI) {
                        emitSignal(BRIDGE_ERROR.name, "oni_name_rejected")
                        return
                    }
                    hideCockpitInternal()
                    emitSignal(ONI_REQUESTED.name, name)
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

    // Private on-device picture selection. Never uploads files or enables WebView content URLs.
    private fun openLocalArtPicker() {
        runOnHostThread {
            val host = activity ?: return@runOnHostThread
            if (galleryPickerPending) return@runOnHostThread
            val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
                addCategory(Intent.CATEGORY_OPENABLE)
                type = "image/*"
                putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("image/png", "image/jpeg", "image/webp"))
                putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            try {
                galleryPickerPending = true
                host.startActivityForResult(intent, LOCAL_ART_PICK_REQUEST)
            } catch (_: ActivityNotFoundException) {
                galleryPickerPending = false
                reportGalleryPickerError("picker_unavailable")
            } catch (_: SecurityException) {
                galleryPickerPending = false
                reportGalleryPickerError("picker_unavailable")
            }
        }
    }

    override fun onMainActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onMainActivityResult(requestCode, resultCode, data)
        if (requestCode != LOCAL_ART_PICK_REQUEST) return
        galleryPickerPending = false
        if (resultCode != Activity.RESULT_OK || data == null) return
        val host = activity ?: return
        val urls = mutableListOf<Uri>()
        data.data?.let { urls.add(it) }
        data.clipData?.let { clip ->
            for (i in 0 until minOf(clip.itemCount, MAX_ART_PICKS)) {
                urls.add(clip.getItemAt(i).uri)
            }
        }
        urls.distinct().take(MAX_ART_PICKS).forEach { uri ->
            try {
                if (uri.scheme != "content") {
                    reportGalleryPickerError("image_format_rejected")
                    return@forEach
                }
                val type = host.contentResolver.getType(uri)
                if (type !in setOf("image/png", "image/jpeg", "image/webp")) {
                    reportGalleryPickerError("image_format_rejected")
                    return@forEach
                }
                val knownSize = host.contentResolver.openAssetFileDescriptor(uri, "r")?.use { it.length } ?: -1L
                if (knownSize > MAX_ART_BYTES) {
                    reportGalleryPickerError("image_too_large")
                    return@forEach
                }
                val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
                host.contentResolver.openInputStream(uri)?.use {
                    BitmapFactory.decodeStream(it, null, bounds)
                }
                if (bounds.outWidth < 1 || bounds.outHeight < 1 ||
                    bounds.outWidth > 12000 || bounds.outHeight > 12000) {
                    reportGalleryPickerError("image_format_rejected")
                    return@forEach
                }
                val opts = BitmapFactory.Options().apply {
                    var factor = 1
                    while (bounds.outWidth / factor > MAX_PREVIEW_EDGE ||
                           bounds.outHeight / factor > MAX_PREVIEW_EDGE) {
                        factor *= 2
                    }
                    inSampleSize = factor
                }
                val bitmap = host.contentResolver.openInputStream(uri)?.use {
                    BitmapFactory.decodeStream(it, null, opts)
                } ?: run {
                    reportGalleryPickerError("image_unreadable")
                    return@forEach
                }
                val buffer = ByteArrayOutputStream()
                val encoded = bitmap.compress(Bitmap.CompressFormat.JPEG, 82, buffer)
                bitmap.recycle()
                if (!encoded || buffer.size() > 3 * 1024 * 1024) {
                    reportGalleryPickerError("image_too_large")
                    return@forEach
                }
                val dataUrl = "data:image/jpeg;base64," +
                    Base64.encodeToString(buffer.toByteArray(), Base64.NO_WRAP)
                val title = uri.lastPathSegment?.takeLast(80) ?: "Private Canon image"
                val js = "window.LuHmCanonGallery&&window.LuHmCanonGallery.addFromNative(" +
                    JSONObject.quote(title) + "," + JSONObject.quote(dataUrl) + ")"
                cockpitView?.evaluateJavascript(js, null)
            } catch (_: Exception) {
                reportGalleryPickerError("image_unreadable")
            }
        }
    }

    private fun reportGalleryPickerError(reason: String) {
        runOnHostThread {
            cockpitView?.evaluateJavascript(
                "window.LuHmCanonGallery&&window.LuHmCanonGallery.nativeError(" +
                    JSONObject.quote(reason) + ")", null
            )
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
