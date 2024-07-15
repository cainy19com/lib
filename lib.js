Object.prototype.getKeyByValue = function (value) {
  for (const key in this)
    if (this[key] == value)
      return key
  return null
}


const $ = document.querySelector.bind(document)
const $$ = document.querySelectorAll.bind(document)
const LOG = console.log.bind(console)


const GV = {} // Global variables
const GF = {} // Global functions
const GC = {} // Global classes


GF.range = n => {
  return [...Array(n).keys()]
}


GF.fetch_ = (api_url, json_data) => {
  return fetch(api_url, {
    method: "POST",
    body: JSON.stringify(json_data),
  }).then(res => {
    if (res.status === 200)
      return res.json()
    else
      throw Error(res.statusText)
  })
}


GF.url_search_params = () => {
  return new URL(window.location.href).searchParams
}


GF.meta = (theme_color = "", title = "") => {
  document.head.innerHTML = `
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="theme-color" content="${theme_color}">
    <title>${title}</title>
    <link rel="icon" href="favicon.ico">
    <link rel="apple-touch-icon" href="apple-touch-icon.png">
    <link rel="stylesheet" href="css/reset.css">
    <link rel="stylesheet" href="css/app.css">
  `
}


GF.is_iphone = () => {
  return /iphone/i.test(window.navigator.userAgent)
}
