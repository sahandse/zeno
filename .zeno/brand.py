from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
source_revision = 'bf841f06c9f01896271b596142a3d846ea9298bd'
def convert(text):
    return (text.replace('Diercohen/foxhole-vpn', 'sahandse/ZENO')
            .replace('DierCohen/foxhole-vpn', 'sahandse/ZENO')
            .replace('io.github.diercohen.foxhole', 'io.github.sahandse.zeno')
            .replace('io_github_diercohen_foxhole', 'io_github_sahandse_zeno').replace('FOXHOLE', 'ZENO').replace('Foxhole', 'Zeno').replace('foxhole', 'zeno'))

for p in list(root.rglob('*')):
    if not p.is_file() or any(x in {'.git', '.zeno', '.github', 'node_modules'} for x in p.relative_to(root).parts) or p.name in {'LICENSE', 'bootstrap.yml'}:
        continue
    try:
        old = p.read_text(encoding='utf-8')
    except (UnicodeError, ValueError):
        continue
    new = convert(old)
    if old != new:
        p.write_text(new, encoding='utf-8')
# Rename native classes, Xcode project entries, package paths and resources together.
for p in sorted(root.rglob('*'), key=lambda p: len(p.parts), reverse=True):
    if any(x in {'.git', '.zeno', '.github', 'node_modules'} for x in p.relative_to(root).parts):
        continue
    name = convert(p.name)
    if name != p.name:
        p.rename(p.with_name(name))
# Android packages and their folders must agree.
java = root / 'mobile/android/app/src/main/java/io/github/diercohen'
if java.exists():
    java.rename(java.with_name('sahandse'))

for rel in ['package.json', 'gui/package.json', 'mobile/package.json']:
    p = root / rel
    data = json.loads(p.read_text())
    if rel != 'mobile/package.json':
        data['version'] = '1.0.0'
        data['author'] = 'Sahand Rezvan'
        data['contributors'] = ['Dier Cohen (Foxhole upstream)']
    if rel == 'package.json':
        data['name'] = '@sahandse/zeno-vpn'
        data['private'] = True
    if rel == 'gui/package.json':
        data['productName'] = data['build']['productName'] = 'Zeno'
        data['build']['linux']['maintainer'] = 'Sahand Rezvan <sahandse@users.noreply.github.com>'
    p.write_text(json.dumps(data, indent=2) + '\n')
# Lockfile root metadata is independent of the dependency resolution.
for rel in ['package-lock.json', 'gui/package-lock.json', 'mobile/package-lock.json']:
    p = root / rel
    lock = json.loads(p.read_text())
    pkg = json.loads((p.parent / 'package.json').read_text())
    lock['name'] = pkg['name']
    if 'version' in pkg:
        lock['version'] = pkg['version']
    if '' in lock.get('packages', {}):
        lock['packages']['']['name'] = pkg['name']
        if 'version' in pkg:
            lock['packages']['']['version'] = pkg['version']
    p.write_text(json.dumps(lock, indent=2) + '\n')
# CLI packages are not published yet. Never install an unrelated public npm package.
p = root / 'src/update.ts'
s = p.read_text().replace('/zeno-vpn/latest`', '/@sahandse%2fzeno-vpn/latest`')
s = s.replace('export function checkUpdate(ways?: Way[]): Promise<void> {',
'''export function checkUpdate(ways?: Way[]): Promise<void> {
  // ZENO CLI is distributed from GitHub, not the public npm registry.
  // An explicit registry is retained for the isolated updater tests.
  if (!process.env.ZENO_REGISTRY) return Promise.resolve();''')
s = s.replace('npm install -g zeno-vpn@latest', 'npm install -g @sahandse/zeno-vpn@latest')
p.write_text(s)
# The fake registry must exercise the same scoped package path as the real updater.
p = root / 'test/ways.test.mjs'
p.write_text(p.read_text().replace('pathname === "/zeno-vpn/latest"', 'pathname === "/@sahandse%2fzeno-vpn/latest"'))
# Signing must be ZENO's. Tag builds must never silently ship a debug-signed APK.
p = root / 'mobile/android/app/build.gradle'
s = p.read_text().replace('android {', '''if (gradle.startParameter.taskNames.any { it.toLowerCase().contains("release") } && !keystore) {
    throw new GradleException("ZENO release requires ZENO_KEYSTORE, ZENO_KEYSTORE_PASSWORD and ZENO_KEY_ALIAS")
}

android {''', 1)
p.write_text(s)
(root / 'UPSTREAM.md').write_text(f'''# Upstream attribution\n\nZENO is derived from [Foxhole VPN](https://github.com/DierCohen/foxhole-vpn),\nrevision `{source_revision}` (version 1.3.3).\n\nCopyright (c) 2026 Dier Cohen. The original MIT license is retained in LICENSE.\nZENO branding and packaging changes: Sahand Rezvan.\nZENO is unofficial and is not affiliated with Mozilla or Foxhole's author.\n''')
readme = root / 'README.md'
readme.rename(root / 'docs/UPSTREAM-USAGE.md')
readme.write_text('''# ZENO\n\nنسخهٔ مستقل مبتنی بر Foxhole VPN با همان رابط و هستهٔ اتصال، برای اندروید، Android TV، ویندوز، مک و لینوکس.\n\n## امکانات\n\n- ورود با حساب Mozilla و انتخاب موقعیت سرور\n- اتصال سراسری TUN و پروکسی SOCKS5/HTTP\n- مسیریابی تفکیکی سایت‌ها و برنامه‌ها؛ اتصال مستقیم سایت‌های ایرانی\n- نمایش مصرف، محافظ تبلیغات و ردیاب، اشتراک اتصال و Smart DNS\n- رابط فارسی و راست‌به‌چپ؛ پشتیبانی از تلویزیون اندرویدی\n- به‌روزرسانی مستقل از مخزن sahandse/ZENO\n\nاین برنامه غیررسمی است. دسترسی سرورها، سهمیه و ورود به حساب تابع سرویس Mozilla و شرایط شبکه است.\n\n## توسعه\n\n```sh\nnpm ci\nnpm test\ncd gui\nnpm ci\nnpm test\nnpm start\n```\n\nراهنمای جزئی امکانات در [راهنمای استفاده](docs/UPSTREAM-USAGE.md) و منشأ کد در [UPSTREAM.md](UPSTREAM.md) قرار دارد.\n\n## ساخت اندروید\n\nاز بخش Actions، گردش‌کار **Android candidate** را اجرا کنید. خروجی آن APK آزمایشی است و برای انتشار فروشگاهی نیست.\nبرای ساخت نسخهٔ انتشار، کلید مستقل ZENO و متغیرهای ZENO_KEYSTORE، ZENO_KEYSTORE_PASSWORD و ZENO_KEY_ALIAS لازم است.\nگردش‌کار Release با تگ نسخه اجرا می‌شود و فقط پیش‌نویس انتشار می‌سازد.\nهنوز آزمون اتصال روی دستگاه واقعی و انتشار عمومی تأیید نشده است.\n''')
