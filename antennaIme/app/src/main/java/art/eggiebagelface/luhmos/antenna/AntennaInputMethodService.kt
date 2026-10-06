package art.eggiebagelface.luhmos.antenna

import android.inputmethodservice.InputMethodService
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.TextView

class AntennaInputMethodService : InputMethodService() {
    private lateinit var heardText: TextView
    private var mode: String = "talk"

    override fun onCreateInputView(): View {
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            gravity = Gravity.CENTER
            setPadding(12, 12, 12, 12)
        }

        heardText = TextView(this).apply {
            text = "heardText: waiting"
            contentDescription = "recognized text preview"
        }
        root.addView(heardText)

        val controls = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        controls.addView(button("Talk") { setMode("talk") })
        controls.addView(button("Command") { setMode("command") })
        controls.addView(button("C ➡") { commitLiteral("C") })
        controls.addView(button("Stop") { commitLiteral("stop") })
        root.addView(controls)

        val keyboard = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL }
        listOf("a", "e", "i", "o", "u", " ").forEach { token ->
            keyboard.addView(button(if (token == " ") "space" else token) { commitLiteral(token) })
        }
        root.addView(keyboard)
        return root
    }

    private fun button(label: String, action: () -> Unit) =
        Button(this).apply { text = label; setOnClickListener { action() } }

    private fun setMode(nextMode: String) {
        mode = nextMode
        heardText.text = "mode: $mode"
    }

    private fun commitLiteral(text: String) {
        currentInputConnection?.commitText(text, 1)
        heardText.text = "heardText: $text"
    }
}
