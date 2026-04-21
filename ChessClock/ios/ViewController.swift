import UIKit
import WebKit
import AppLovinSDK
import StoreKit

// -------------------------------------------------------
// GameConfig — copy this file into each game's iOS project
// and fill in the constants below.
// -------------------------------------------------------
struct GameConfig {
    // AppLovin MAX ad unit IDs — create at dash.applovin.com → Ad Units
    static let bannerUnitId       = "ENTER_YOUR_MAX_BANNER_UNIT_ID"
    static let interstitialUnitId = "ENTER_YOUR_MAX_INTER_UNIT_ID"
    static let rewardedUnitId     = "ENTER_YOUR_MAX_REWARDED_UNIT_ID"

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
// WKWebView + AppLovin MAX + StoreKit 2
// The iOS WKWebView bridge injects window.Android so the
// game HTML works without any changes — same JS on both platforms.
// -------------------------------------------------------
class ViewController: UIViewController {

    private var webView: WKWebView!
    private var bannerAd: MAAdView!
    private var interstitialAd: MAInterstitialAd!
    private var rewardedAd: MARewardedAd!
    private var pendingRewardType: String?
    private var bannerHeightConstraint: NSLayoutConstraint?

    // MARK: - Lifecycle

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = GameConfig.webViewBackground
        setupWebView()
        setupBannerAd()
        initAppLovinMax()
    }

    override var prefersStatusBarHidden: Bool { true }
    override var prefersHomeIndicatorAutoHidden: Bool { true }

    // MARK: - WebView Setup

    private func setupWebView() {
        let config = WKWebViewConfiguration()
        config.mediaTypesRequiringUserActionForPlayback = []

        // Inject window.Android shim so game.html works unchanged on iOS
        // All method calls are forwarded to the native "bridge" message handler
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

    // MARK: - AppLovin MAX

    private func initAppLovinMax() {
        ALSdk.shared().initialize { [weak self] _ in
            DispatchQueue.main.async {
                self?.bannerAd.loadAd()
                self?.loadInterstitialAd()
                self?.loadRewardedAd()
            }
        }
    }

    // MARK: - Banner

    private func setupBannerAd() {
        bannerAd = MAAdView(adUnitIdentifier: GameConfig.bannerUnitId)
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
        interstitialAd = MAInterstitialAd(adUnitIdentifier: GameConfig.interstitialUnitId)
        interstitialAd.delegate = self
        interstitialAd.load()
    }

    private func showInterstitialAd() {
        DispatchQueue.main.async {
            if self.interstitialAd?.isReady == true {
                self.interstitialAd.show()
            }
        }
    }

    // MARK: - Rewarded

    private func loadRewardedAd() {
        rewardedAd = MARewardedAd.shared(withAdUnitIdentifier: GameConfig.rewardedUnitId)
        rewardedAd.delegate = self
        rewardedAd.load()
    }

    private func showRewardedAd(type: String) {
        guard GameConfig.validRewardTypes.contains(type) else { return }
        pendingRewardType = type
        DispatchQueue.main.async {
            if self.rewardedAd?.isReady == true {
                self.rewardedAd.show()
            } else {
                self.evaluateJS("window.onAdNotReady && window.onAdNotReady();")
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

// MARK: - MAAdViewAdDelegate (Banner)

extension ViewController: MAAdViewAdDelegate {
    func didLoad(_ ad: MAAd) { }
    func didFailToLoadAd(forAdUnitIdentifier adUnitIdentifier: String, withError error: MAError) { }
    func didDisplay(_ ad: MAAd) { }
    func didHide(_ ad: MAAd) { }
    func didClick(_ ad: MAAd) { }
    func didFail(toDisplay ad: MAAd, withError error: MAError) { }
    func didExpand(_ ad: MAAd) { }
    func didCollapse(_ ad: MAAd) { }
}

// MARK: - MAAdDelegate (Interstitial)

extension ViewController: MAAdDelegate {
    func didLoad(_ ad: MAAd) {
        // Ad ready — nothing needed, isReady checks handle gating
    }

    func didFailToLoadAd(forAdUnitIdentifier adUnitIdentifier: String, withError error: MAError) {
        // Retry will happen on next show attempt
    }

    func didDisplay(_ ad: MAAd) { }

    func didHide(_ ad: MAAd) {
        // Preload next ad after dismissal
        if ad.adUnitIdentifier == GameConfig.interstitialUnitId {
            interstitialAd.load()
        } else if ad.adUnitIdentifier == GameConfig.rewardedUnitId {
            rewardedAd.load()
        }
    }

    func didClick(_ ad: MAAd) { }

    func didFail(toDisplay ad: MAAd, withError error: MAError) {
        if ad.adUnitIdentifier == GameConfig.interstitialUnitId {
            interstitialAd.load()
        } else if ad.adUnitIdentifier == GameConfig.rewardedUnitId {
            rewardedAd.load()
            evaluateJS("window.onAdNotReady && window.onAdNotReady();")
        }
    }
}

// MARK: - MARewardedAdDelegate

extension ViewController: MARewardedAdDelegate {
    func didRewardUser(for ad: MAAd, with reward: MAReward) {
        guard let rewardType = pendingRewardType else { return }
        // CRITICAL: reward granted ONCE here only — not in didHide
        evaluateJS("window.onAdReward && window.onAdReward('\(rewardType)');")
        pendingRewardType = nil
    }
    func didStartRewardedVideo(for ad: MAAd) { }
    func didCompleteRewardedVideo(for ad: MAAd) { }
}
