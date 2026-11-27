package io.github.sahandse.zeno

import android.webkit.WebView
import com.facebook.react.BaseReactPackage
import com.facebook.react.bridge.NativeModule
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.module.model.ReactModuleInfo
import com.facebook.react.module.model.ReactModuleInfoProvider

/** The window's way to the core (specs/NativeZeno.ts): its lines both ways. */
class ZenoModule(context: ReactApplicationContext) : NativeZenoSpec(context) {
  private val listener: (String) -> Unit = { emitOnLine(it) }

  override fun getName() = NAME

  override fun start() {
    Core.listener = listener
    Core.start(reactApplicationContext)
  }

  override fun send(line: String) = Core.send(line)

  override fun webView(): String = WebView.getCurrentWebViewPackage()?.let { "${it.packageName} ${it.versionName}" } ?: ""

  override fun page() = "file:///android_asset/www/renderer/index.html" // scripts/prepare.mjs puts it there

  override fun moveToBack() {
    reactApplicationContext.currentActivity?.moveTaskToBack(true)
  }

  override fun invalidate() {
    if (Core.listener === listener) Core.listener = null
    super.invalidate()
  }

  companion object {
    const val NAME = "Zeno"
  }
}

class ZenoPackage : BaseReactPackage() {
  override fun getModule(name: String, reactContext: ReactApplicationContext): NativeModule? =
    if (name == ZenoModule.NAME) ZenoModule(reactContext) else null

  override fun getReactModuleInfoProvider() = ReactModuleInfoProvider {
    mapOf(ZenoModule.NAME to ReactModuleInfo(ZenoModule.NAME, ZenoModule.NAME, false, false, false, true))
  }
}
