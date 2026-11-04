const VALID_PRODUCTS = new Set([
  'remove_ads','coins_small','coins_medium','coins_large','coins_mega',
  'hint_pack','five_lives','unlimited_lives_1h','unlimited_lives_forever',
  'starter_pack','season_pass_monthly','weekly_pass'
]);
const VALID_REWARD_TYPES = new Set(['hint','skip','life','extra_life','free_coins']);

// Canonical shop order (CLAUDE.md "Shop ordering"): Spend Your Coins →
// Coin packs → Subscriptions (Season Pass injected after coins_mega) → IAPs.
// Lives are only used by Endless grids; campaign levels + the Daily are free.
const SHOP_PRODUCTS = [
  {id:'lives_5_coins',    icon:'🪙', name:'5 Lives (Coins)',       desc:'Spend 30 coins for 5 lives for Endless grids', price:'30 🪙', coinCost:30},
  {id:'coins_small',      icon:'🪙', name:'100 Coins',            desc:'For hints, Endless lives and themes',    price:'$0.99'},
  {id:'coins_medium',     icon:'💵', name:'400 Coins',            desc:'For hints, Endless lives and themes',    price:'$2.99'},
  {id:'coins_large',      icon:'💰', name:'800 Coins',            desc:'Great value coin pack',                  price:'$4.99'},
  {id:'coins_mega',       icon:'🏆', name:'2000 Coins',           desc:'Mega coin pack — most coins per dollar', price:'$9.99'},
  {id:'starter_pack',     icon:'🎁', name:'Starter Pack',         desc:'100🪙 + 5 hints + 5 lives + Ads Off',   price:'$0.99'},
  {id:'remove_ads',       icon:'🚫', name:'Remove Ads',           desc:'No banner or interstitial ads, forever', price:'$2.99'},
  {id:'hint_pack',        icon:'💡', name:'10 Hints',             desc:'Each flashes the first letter of a word you still need', price:'$1.99'},
  {id:'five_lives',       icon:'❤️', name:'5 Extra Lives',        desc:'Refill the lives Endless grids use',     price:'$0.99'},
  {id:'unlimited_lives_1h',icon:'⚡',name:'Unlimited Lives 1hr',  desc:'Endless grids cost no life for 1 hour',  price:'$1.99'},
  {id:'unlimited_lives_forever',icon:'♾️',name:'Unlimited Lives Forever',desc:'Endless grids never cost a life', price:'$4.99'}
];
