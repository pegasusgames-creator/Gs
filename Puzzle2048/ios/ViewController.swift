import UIKit
import WebKit
import GoogleMobileAds
import UserMessagingPlatform
import AppTrackingTransparency
import StoreKit

// -------------------------------------------------------
// GameConfig — copy this file into each game's iOS project
// and fill in the constants below.
// -------------------------------------------------------
struct GameConfig {
    // AdMob ad unit IDs — the SAME unit IDs the Android AdMob app uses
    // (apps.admob.com → this app → Ad Units). NOTE: AdMob serves these by
    // platform, so create iOS-platform units in the same AdMob app if fill
    // is low; the IDs below mirror the Android build per the migration spec.
    static let bannerUnitId       = "ca-app-pub-5695494884863768/8535411813"
    static let interstitialUnitId = "ca-app-pub-5695494884863768/8333515691"
    static let rewardedUnitId     = "ca-app-pub-5695494884863768/6020929115"

    // StoreKit product IDs — must match App Store Connect
    static let validProducts: Set<String> = [
        "remove_ads", "coins_small", "coins_large",
        "unlimited_undos", "five_lives", "unlimited_lives_1h", "unlimited_lives_forever"
    ]

    // Valid reward types — prevents message-handler abuse
    static let validRewardTypes: Set<String> = ["undo", "skip", "life"]

    // WebView background color (prevents white flash before game loads)
    // Match your game.html body background-color
    static let webViewBackground = UIColor(red: 26/255, green: 26/255, blue: 46/255, alpha: 1)

    // HTML file name inside the app bundle
    static let gameFile = "game"   // loads game.html
}

// -------------------------------------------------------
// ViewController
// WKWebView + Google Mobile Ads (AdMob) + UMP consent + ATT + StoreKit 2
// The iOS WKWebView bridge injects window.Android so the game HTML works
// without any changes — same JS on both platforms.
// -------------------------------------------------------
class ViewController: UIViewController {

    private var webView: WKWebView!
    private var bannerAd: GADBannerView!
    private var interstitialAd: GADInterstitialAd?
    private var rewardedAd: GADRewardedAd?
    private var pendingRewardType: String?
    private var adsStarted = false

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = GameConfig.webViewBackground
        setupWebView()
        setupBannerAd()
        gatherConsentThenStartAds()
    }

    override var prefersStatusBarHidden: Bool { true }
    override var prefersHomeIndicatorAutoHidden: Bool { true }

    // MARK: - WebView Setup

    private func setupWebView() {
        let config = WKWebViewConfiguration()
        config.mediaTypesRequiringUserActionForPlayback = []

        // Inject window.Android shim so game.html works unchanged on iOS.
        // All method calls are forwarded to the native "bridge" message handler.
        let bridgeJS = """
        window.Android = {
            showInterstitial: function() {
                window.webkit.messageHandlers.bridge.postMessage({action:'showInterstitial'});
            },
            showRewarded: function(type) {
                window.webkit.messageHandlers.bridge.postMessage({action:'showRewarded', type:type});
            },
            purchase: function(productId) {
                window.webkit.messageHandlers.bridge.postMessage({action:'purchase', productId:productId});
            },
            hideBannerAd: function() {
                window.webkit.messageHandlers.bridge.postMessage({action:'hideBannerAd'});
            },
            showBannerAd: function() {
                window.webkit.messageHandlers.bridge.postMessage({action:'showBannerAd'});
            },
            log: function(msg) {},
            logEvent: function(name, params) {
                window.webkit.messageHandlers.bridge.postMessage({action:'logEvent', name:name, params:params});
            }
        };
        window.NativeBridge = window.Android;
        """
        let script = WKUserScript(source: bridgeJS, injectionTime: .atDocumentStart, forMainFrameOnly: false)
        config.userContentController.addUserScript(script)
        config.userContentController.add(self, name: "bridge")

        webView = WKWebView(frame: .zero, configuration: config)
        webView.scrollView.isScrollEnabled = false
        webView.scrollView.bounces = false
        webView.backgroundColor = GameConfig.webViewBackground
        webView.isOpaque = false
        webView.navigationDelegate = self
        webView.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(webView)

        // Load game.html from bundle
        if let gameURL = Bundle.main.url(forResource: GameConfig.gameFile, withExtension: "html") {
            webView.loadFileURL(gameURL, allowingReadAccessTo: gameURL.deletingLastPathComponent())
        }
    }

    // MARK: - Consent (UMP) + ATT, then start ads

    // Gather Google UMP consent and request App Tracking Transparency BEFORE
    // the first ad loads / before MobileAds starts (EEA + Apple requirements).
    private func gatherConsentThenStartAds() {
        let params = UMPRequestParameters()
        params.tagForUnderAgeOfConsent = false
        #if DEBUG
        let dbg = UMPDebugSettings()
        dbg.geography = .EEA
        params.debugSettings = dbg
        #endif
        UMPConsentInformation.sharedInstance.requestConsentInfoUpdate(with: params) { [weak self] _ in
            guard let self = self else { return }
            UMPConsentForm.loadAndPresentIfRequired(from: self) { [weak self] _ in
                self?.requestATTThenStart()
            }
        }
    }

    private func requestATTThenStart() {
        if #available(iOS 14, *) {
            ATTrackingManager.requestTrackingAuthorization { [weak self] _ in
                DispatchQueue.main.async { self?.startAds() }
            }
        } else {
            startAds()
        }
    }

    private func startAds() {
        guard !adsStarted else { return }
        adsStarted = true
        GADMobileAds.sharedInstance().start { [weak self] _ in
            DispatchQueue.main.async {
                self?.bannerAd.load(GADRequest())
                self?.loadInterstitialAd()
                self?.loadRewardedAd()
            }
        }
    }

    // MARK: - Banner

    private func setupBannerAd() {
        bannerAd = GADBannerView(adSize: GADAdSizeBanner)
        bannerAd.adUnitID = GameConfig.bannerUnitId
        bannerAd.rootViewController = self
        bannerAd.delegate = self
        bannerAd.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(bannerAd)

        let bannerHeight: CGFloat = 50

        NSLayoutConstraint.activate([
            // Banner pinned to bottom safe area
            bannerAd.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            bannerAd.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            bannerAd.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
            bannerAd.heightAnchor.constraint(equalToConstant: bannerHeight),

            // WebView fills everything above the banner
            webView.topAnchor.constraint(equalTo: view.topAnchor),
            webView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            webView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            webView.bottomAnchor.constraint(equalTo: bannerAd.topAnchor)
        ])
    }

    private func hideBanner() {
        DispatchQueue.main.async { self.bannerAd.isHidden = true }
    }

    private func showBanner() {
        DispatchQueue.main.async { self.bannerAd.isHidden = false }
    }

    // MARK: - Interstitial

    private func loadInterstitialAd() {
        GADInterstitialAd.load(withAdUnitID: GameConfig.interstitialUnitId,
                               request: GADRequest()) { [weak self] ad, error in
            guard let self = self, error == nil else { return }
            self.interstitialAd = ad
            self.interstitialAd?.fullScreenContentDelegate = self
        }
    }

    private func showInterstitialAd() {
        DispatchQueue.main.async {
            guard let ad = self.interstitialAd else { return }
            ad.present(fromRootViewController: self)
        }
    }

    // MARK: - Rewarded

    private func loadRewardedAd() {
        GADRewardedAd.load(withAdUnitID: GameConfig.rewardedUnitId,
                           request: GADRequest()) { [weak self] ad, error in
            guard let self = self, error == nil else { return }
            self.rewardedAd = ad
            self.rewardedAd?.fullScreenContentDelegate = self
        }
    }

    private func showRewardedAd(type: String) {
        guard GameConfig.validRewardTypes.contains(type) else { return }
        pendingRewardType = type
        DispatchQueue.main.async {
            guard let ad = self.rewardedAd else {
                self.evaluateJS("window.onAdNotReady && window.onAdNotReady();")
                return
            }
            ad.present(fromRootViewController: self) { [weak self] in
                // CRITICAL: reward granted ONCE here only (user earned reward).
                guard let self = self, let rewardType = self.pendingRewardType else { return }
                self.evaluateJS("window.onAdReward && window.onAdReward('\(rewardType)');")
                self.pendingRewardType = nil
            }
        }
    }

    // MARK: - StoreKit 2 IAP

    private func purchaseProduct(_ productId: String) {
        guard GameConfig.validProducts.contains(productId) else { return }
        Task {
            do {
                let products = try await Product.products(for: [productId])
                guard let product = products.first else { return }
                let result = try await product.purchase()
                switch result {
                case .success(let verification):
                    switch verification {
                    case .verified(let transaction):
                        await transaction.finish()
                        await MainActor.run {
                            self.evaluateJS("window.onPurchaseComplete && window.onPurchaseComplete('\(productId)');")
                            if productId == "remove_ads" { self.hideBanner() }
                        }
                    case .unverified:
                        break
                    }
                case .userCancelled, .pending:
                    break
                @unknown default:
                    break
                }
            } catch {
                // Purchase failed — ignore, UI already handles this
            }
        }
    }

    private func restorePurchases() {
        Task {
            do {
                try await AppStore.sync()
                for await result in Transaction.currentEntitlements {
                    if case .verified(let transaction) = result {
                        await MainActor.run {
                            self.evaluateJS("window.onPurchaseComplete && window.onPurchaseComplete('\(transaction.productID)');")
                            if transaction.productID == "remove_ads" { self.hideBanner() }
                        }
                    }
                }
            } catch {
                // Restore failed silently
            }
        }
    }

    // MARK: - JS Helpers

    private func evaluateJS(_ js: String) {
        DispatchQueue.main.async {
            self.webView.evaluateJavaScript(js)
        }
    }
}

// MARK: - WKScriptMessageHandler (native bridge receiver)

extension ViewController: WKScriptMessageHandler {
    func userContentController(_ userContentController: WKUserContentController,
                                didReceive message: WKScriptMessage) {
        guard message.name == "bridge",
              let body = message.body as? [String: Any],
              let action = body["action"] as? String else { return }

        switch action {
        case "showInterstitial":
            showInterstitialAd()

        case "showRewarded":
            if let type = body["type"] as? String {
                showRewardedAd(type: type)
            }

        case "purchase":
            if let productId = body["productId"] as? String {
                purchaseProduct(productId)
            }

        case "hideBannerAd":
            hideBanner()

        case "showBannerAd":
            showBanner()

        case "logEvent":
            // Optional: add Firebase Analytics for iOS here
            break

        default:
            break
        }
    }
}

// MARK: - WKNavigationDelegate

extension ViewController: WKNavigationDelegate {
    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // Signal game that native SDK is ready (same callback as Android)
        evaluateJS("window.onAdMobLoaded && window.onAdMobLoaded();")
    }
}

// MARK: - GADBannerViewDelegate

extension ViewController: GADBannerViewDelegate {
    func bannerViewDidReceiveAd(_ bannerView: GADBannerView) { }
    func bannerView(_ bannerView: GADBannerView, didFailToReceiveAdWithError error: Error) { }
}

// MARK: - GADFullScreenContentDelegate (interstitial + rewarded)

extension ViewController: GADFullScreenContentDelegate {
    func adDidDismissFullScreenContent(_ ad: GADFullScreenPresentingAd) {
        // Preload the next interstitial + rewarded after dismissal.
        loadInterstitialAd()
        loadRewardedAd()
    }

    func ad(_ ad: GADFullScreenPresentingAd, didFailToPresentFullScreenContentWithError error: Error) {
        loadInterstitialAd()
        loadRewardedAd()
        evaluateJS("window.onAdNotReady && window.onAdNotReady();")
    }
}
