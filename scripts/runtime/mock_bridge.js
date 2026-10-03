// Injected before every page script: a stand-in for the Java `Android`
// bridge that records every call in window.__calls. Return values can be
// overridden per test via window.__mockRet = {method: value} (set first).
(function(){
  window.__calls = [];
  const ret = Object.assign({
    isPurchased: false, isAppInstalled: false, getNotificationsEnabled: true,
    hasNotificationPermission: true, isPlayGamesAuthenticated: false,
  }, window.__mockRet || {});
  const handler = {
    get(t, p) {
      if (typeof p !== 'string') return undefined;
      return function(...args){
        window.__calls.push([p, args.map(a => typeof a === 'string' ? a.slice(0, 80) : a)]);
        return p in ret ? ret[p] : undefined;
      };
    },
    has() { return true; }
  };
  // Like the real gin bridge, method reads always resolve to the bridge —
  // a JS assignment (monkey-patch) does NOT shadow them.
  window.Android = new Proxy({}, handler);
  window.NativeBridge = window.Android;
  window.alert = (m) => window.__calls.push(['alert', [String(m).slice(0, 120)]]);
  window.confirm = (m) => { window.__calls.push(['confirm', [String(m).slice(0, 120)]]); return false; };
  window.prompt = () => null;
})();
