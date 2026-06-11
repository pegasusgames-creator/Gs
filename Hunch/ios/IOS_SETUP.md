# iOS App Setup Guide

## Requirements
- Mac with Xcode 15+
- Apple Developer account ($99/year — needed for App Store)
- CocoaPods (`sudo gem install cocoapods`)

## One-time setup: AppLovin MAX

1. Go to dash.applovin.com → Sign up / Log in
2. Create a new iOS app
3. Create 3 Ad Units: Banner, Interstitial, Rewarded
4. Copy the Ad Unit IDs into `ViewController.swift` → `GameConfig`
5. Copy your SDK Key (dash.applovin.com → Account → Keys) into `Info.plist`

## Per-game steps

### 1. Create Xcode project (do this on Mac)
```
File → New → Project → iOS → App
Product Name: <YourAppName>  (use the folder name)
Bundle Identifier: com.pegasusgames.<yourapp>
Language: Swift
Interface: Storyboard (then delete storyboard — we use code-based UI)
```

### 2. Delete auto-generated files
- Delete `Main.storyboard`
- Delete `ViewController.swift` (we provide ours)
- In `Info.plist`: remove `NSPrincipalClass` → `NSStoryboard` key
- In `Info.plist`: remove `UIMainStoryboardFile` key

### 3. Copy template files into the project
```
cp _template/ios/AppDelegate.swift   YourGame/
cp _template/ios/ViewController.swift YourGame/
cp _template/ios/Info.plist          YourGame/
```
Add all 3 files to the Xcode target.

### 4. Copy game HTML
```
cp android/app/src/main/assets/game.html  YourGame/
```
In Xcode: drag `game.html` into the project → "Add to target" ✓

### 5. Install CocoaPods
```
cp _template/ios/Podfile  YourGame/Podfile
# Edit Podfile: replace 'GameApp' with your Xcode target name
cd YourGame
pod install
open YourGame.xcworkspace  # always use .xcworkspace after pod install
```

### 6. Fill in the constants
In `ViewController.swift`, update `GameConfig`:
```swift
static let bannerUnitId       = "your-max-banner-unit-id"
static let interstitialUnitId = "your-max-inter-unit-id"
static let rewardedUnitId     = "your-max-rewarded-unit-id"
static let webViewBackground  = UIColor(red: 26/255, green: 26/255, blue: 46/255, alpha: 1)
```

In `Info.plist`:
```
AppLovinSdkKey      → your AppLovin SDK key
GADApplicationIdentifier → your AdMob iOS app ID
CFBundleDisplayName → Your App Name
CFBundleIdentifier  → com.pegasusgames.yourgame
```

### 7. Add GoogleService-Info.plist (for AdMob adapter)
- Firebase Console → Add iOS app → download `GoogleService-Info.plist`
- Drag into Xcode project → Add to target ✓

### 8. Build & Archive
- Select a device or simulator → Product → Build (⌘B)
- For App Store: Product → Archive → Distribute App → App Store Connect

## Building from Linux (CI/CD)

Since you're on Linux, use **Codemagic** for iOS builds:
1. Push your game folder to GitHub
2. Sign up at codemagic.io → Connect GitHub
3. Free tier: 500 build minutes/month
4. Codemagic runs Xcode on their Mac fleet and delivers a signed IPA

Alternative: **GitHub Actions** with `macos-latest` runner (2000 minutes free/month).

## App Store IAP Setup
- App Store Connect → Your App → Features → In-App Purchases
- Add products with the SAME product IDs as your `GameConfig.validProducts`
- Must complete bank/tax setup before IAP can be approved
