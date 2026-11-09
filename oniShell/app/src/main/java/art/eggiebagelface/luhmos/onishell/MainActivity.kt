package art.eggiebagelface.luhmos.onishell

import android.app.Activity
import android.app.role.RoleManager
import android.content.ActivityNotFoundException
import android.content.ComponentName
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.content.pm.ResolveInfo
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.BatteryManager
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.Settings
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.View
import android.view.WindowInsets
import android.widget.*
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * A normal, reversible Android Home launcher.
 * It does not modify Samsung SystemUI, switch recents, require root, or
 * acquire administrative privileges.
 */
class MainActivity : Activity() {
    private val bg = Color.rgb(16, 13, 28)
    private val panel = Color.rgb(32, 26, 52)
    private val magenta = Color.rgb(255, 89, 218)
    private val cyan = Color.rgb(81, 242, 237)
    private val text = Color.rgb(244, 240, 252)
    private val muted = Color.rgb(171, 159, 192)
    private lateinit var grid: GridLayout
    private lateinit var clock: TextView
    private lateinit var status: TextView
    private val ticker = Handler(Looper.getMainLooper())
    private var visible = false
    private var apps: List<ResolveInfo> = emptyList()
    private var searchQuery = ""
    private val tick = object : Runnable {
        override fun run() {
            if (!visible) return
            val time = SimpleDateFormat("EEE · HH:mm", Locale.getDefault()).format(Date())
            clock.text = time
            status.text = "● LOCAL MODE  ·  BATTERY ${batteryPercent()}%"
            ticker.postDelayed(this, 30_000)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        window.statusBarColor = bg
        window.navigationBarColor = bg

        val background = GradientDrawable(
            GradientDrawable.Orientation.TL_BR,
            intArrayOf(Color.rgb(38, 15, 61), bg, Color.rgb(12, 24, 43))
        )
        val scroll = ScrollView(this).apply {
            fillViewport = true
            this.background = background
        }
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(20), dp(12), dp(20), dp(28))
        }
        scroll.addView(root)
        setContentView(scroll)
        // Android 15+ edge-to-edge: keep controls away from system bars.
        scroll.setOnApplyWindowInsetsListener { view, insets ->
            val bars = insets.getInsets(WindowInsets.Type.systemBars())
            view.setPadding(bars.left, bars.top, bars.right, bars.bottom)
            insets
        }

        val title = label("◈  LUHM / ONI SHELL", 22f, text, Typeface.BOLD)
        root.addView(title)
        clock = label("", 15f, cyan, Typeface.NORMAL)
        root.addView(clock)
        status = label("● LOCAL MODE", 11f, muted, Typeface.BOLD)
        root.addView(status)
        root.addView(gap(18))

        root.addView(label("YOUR TABLET. YOUR DOMAIN.", 19f, magenta, Typeface.BOLD))
        root.addView(label("Creative cockpit · native Android desktop · zero firmware changes",
            12f, muted, Typeface.NORMAL))
        root.addView(gap(18))

        val quick = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        quick.addView(action("◈  OPEN LUHM", true) {
            startActivity(Intent(this, CockpitActivity::class.java))
        }, weighted())
        quick.addView(gap(8))
        quick.addView(action("⚙  SETTINGS", false) {
            try { startActivity(Intent(Settings.ACTION_SETTINGS)) }
            catch (_: ActivityNotFoundException) { toast("Settings unavailable") }
        }, weighted())
        root.addView(quick)
        root.addView(gap(9))
        root.addView(action("⌂  SET AS HOME  ·  TAP TO CHOOSE", false) {
            requestHomeRole()
        }, LinearLayout.LayoutParams(-1, dp(48)))
        root.addView(gap(24))

        root.addView(label("APPLICATION DECK", 18f, cyan, Typeface.BOLD))
        val search = EditText(this).apply {
            hint = "Search installed apps…"
            setHintTextColor(muted)
            setTextColor(text)
            singleLine = true
            textSize = 15f
            setPadding(dp(16), dp(9), dp(16), dp(9))
            background = box(panel, 16, Color.rgb(82, 51, 112))
            inputType = android.text.InputType.TYPE_CLASS_TEXT
        }
        root.addView(search, LinearLayout.LayoutParams(-1, dp(51)))
        root.addView(gap(13))

        grid = GridLayout(this).apply {
            columnCount = if (resources.displayMetrics.widthPixels /
                    resources.displayMetrics.density >= 700) 6 else 4
            alignmentMode = GridLayout.ALIGN_BOUNDS
            useDefaultMargins = true
        }
        root.addView(grid)
        root.addView(gap(24))
        root.addView(label("ONI SHELL · SOURCE CANDIDATE 0.1", 10f, muted, Typeface.NORMAL))

        search.addTextChangedListener(object : TextWatcher {
            override fun afterTextChanged(s: Editable?) {
                searchQuery = s?.toString().orEmpty()
                showApps(searchQuery)
            }
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {}
        })
        refreshApps()
    }

    override fun onResume() {
        super.onResume()
        visible = true
        ticker.removeCallbacks(tick)
        ticker.post(tick)
        refreshApps()
    }
    override fun onPause() {
        visible = false
        ticker.removeCallbacks(tick)
        super.onPause()
    }

    private fun refreshApps() {
        val intent = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        apps = packageManager.queryIntentActivities(intent, 0)
            .filter { it.activityInfo?.packageName != packageName }
            .sortedBy { it.loadLabel(packageManager).toString().lowercase(Locale.getDefault()) }
        if (::grid.isInitialized) showApps(searchQuery)
    }

    private fun showApps(filter: String) {
        grid.removeAllViews()
        val filtered = apps.filter {
            it.loadLabel(packageManager).toString().contains(filter, ignoreCase = true)
        }
        val count = grid.columnCount
        val widthDp = (resources.displayMetrics.widthPixels /
                resources.displayMetrics.density).toInt()
        val tileWidth = ((widthDp - 56) / count - 10).coerceIn(72, 150)
        filtered.forEachIndexed { index, app ->
            val item = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
                gravity = Gravity.CENTER
                setPadding(dp(5), dp(12), dp(5), dp(7))
                background = box(panel, 15, Color.rgb(65, 42, 88))
                isClickable = true
                isFocusable = true
                contentDescription = "Launch ${app.loadLabel(packageManager)}"
                setOnClickListener { launch(app) }
            }
            val icon = ImageView(this).apply {
                setImageDrawable(app.loadIcon(packageManager))
                scaleType = ImageView.ScaleType.FIT_CENTER
            }
            item.addView(icon, LinearLayout.LayoutParams(dp(42), dp(42)))
            item.addView(gap(8))
            val name = label(app.loadLabel(packageManager).toString(), 11f, text, Typeface.NORMAL)
            name.gravity = Gravity.CENTER
            name.maxLines = 2
            name.ellipsize = android.text.TextUtils.TruncateAt.END
            item.addView(name)
            val cell = GridLayout.LayoutParams(
                GridLayout.spec(index / count), GridLayout.spec(index % count))
            cell.width = dp(tileWidth)
            cell.height = dp(106)
            cell.setMargins(dp(3), dp(4), dp(3), dp(4))
            grid.addView(item, cell)
        }
        if (filtered.isEmpty()) {
            val empty = label("No matching apps", 14f, muted, Typeface.NORMAL)
            grid.addView(empty)
        }
    }

    private fun launch(app: ResolveInfo) {
        val activity = app.activityInfo ?: return
        val launch = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_LAUNCHER)
            component = ComponentName(activity.packageName, activity.name)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_RESET_TASK_IF_NEEDED)
        }
        try { startActivity(launch) }
        catch (_: Exception) { toast("Could not launch this app") }
    }

    private fun requestHomeRole() {
        val manager = getSystemService(RoleManager::class.java)
        if (manager.isRoleAvailable(RoleManager.ROLE_HOME)) {
            if (manager.isRoleHeld(RoleManager.ROLE_HOME)) {
                toast("ONI SHELL is already your Home app")
            } else {
                startActivityForResult(manager.createRequestRoleIntent(RoleManager.ROLE_HOME), 1)
            }
        } else {
            try { startActivity(Intent(Settings.ACTION_HOME_SETTINGS)) }
            catch (_: Exception) { toast("Home selection not available") }
        }
    }

    private fun batteryPercent(): Int {
        val battery = registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = battery?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = battery?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        return if (level >= 0 && scale > 0) level * 100 / scale else 0
    }

    private fun action(caption: String, highlighted: Boolean, callback: () -> Unit): TextView =
        label(caption, 13f, if (highlighted) bg else text, Typeface.BOLD).apply {
            gravity = Gravity.CENTER
            background = box(if (highlighted) cyan else panel, 16,
                if (highlighted) cyan else magenta)
            setOnClickListener { callback() }
            isFocusable = true
        }

    private fun label(value: String, size: Float, color: Int, weight: Int): TextView =
        TextView(this).apply {
            text = value
            textSize = size
            setTextColor(color)
            typeface = Typeface.create("sans-serif", weight)
            includeFontPadding = true
        }

    private fun weighted() = LinearLayout.LayoutParams(0, dp(54), 1f)
    private fun gap(height: Int) = View(this).apply {
        layoutParams = LinearLayout.LayoutParams(dp(height), dp(height))
    }
    private fun dp(value: Int): Int = (value * resources.displayMetrics.density + 0.5f).toInt()
    private fun box(color: Int, radius: Int, stroke: Int): GradientDrawable =
        GradientDrawable().apply {
            setColor(color); cornerRadius = dp(radius).toFloat()
            setStroke(dp(1), stroke)
        }
    private fun toast(message: String) =
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}
