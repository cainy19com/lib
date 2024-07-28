// 
Object.prototype.getKeyByValue = function (value) {
  for (const key in this)
    if (this[key] === value)
      return key
  return null
}


// 
const $ = document.querySelector.bind(document)
const $$ = document.querySelectorAll.bind(document)
const LOG = console.log.bind(console)


const QS = (se, el = document) => el.querySelector(se)
const QSA = (se, el = document) => el.querySelectorAll(se)


// 
const GV = {} // Global variables
const GF = {} // Global functions
const GC = {} // Global classes


// 
GF.range = n => {
  return [...Array(n).keys()]
}


GF.fetch = (api_url, json_data) => {
  return fetch(api_url, {
    method: "POST",
    body: JSON.stringify(json_data),
  }).then(res => {
    if (res.status === 200)
      return res.json()
    else
      return { code: 1, msg: res.statusText }
  })
}


GF.url_search_params = () => {
  return new URL(window.location.href).searchParams
}


GF.set_theme_color = color => {
  $(`meta[name="theme-color"]`).content = color
}


GF.is_iphone = () => {
  return /iphone/i.test(window.navigator.userAgent)
}


GF.b_to_kb = (bytes, round) => {
  const kb = bytes / 1024
  const ro = kb.toFixed(round)
  if (ro < kb)
    ro = (ro + 1 / 10 ** round).toFixed(round)
  return ro
}


GF.b_to_mb = (bytes, round) => {
  const mb = bytes / 1024 / 1024
  const ro = mb.toFixed(round)
  if (ro < mb)
    ro = (ro + 1 / 10 ** round).toFixed(round)
  return ro
}

