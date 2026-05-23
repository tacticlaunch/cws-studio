// CWS bulk locale full-description uploader.
// Use on the extension's "Store Listing" page in the CWS developer dashboard.
// Steps: open the Store Listing page, refresh it, open DevTools -> Console
// (type `allow pasting` first if Chrome blocks pasting), paste this whole
// script, press Enter, then click "Choose Files" in the green box and select
// your extension's `_locales` folder. It reads _locales/<code>/messages.json ->
// storeDesc.message and fills the 16,000-char description textarea for every
// locale via the CWS language dropdown. Afterwards click "Save draft", refresh,
// and verify each language loaded.

const ANIMATION_TIMEOUT = 500

const fileInput = document.createElement('input')
fileInput.setAttribute("id", "filepicker")
fileInput.setAttribute("type", 'file')
fileInput.setAttribute("webkitdirectory", '')
fileInput.setAttribute("multiple", '')
fileInput.setAttribute("style", 'position: absolute;top: 0;z-index: 999;padding: 1rem;background: green;')
document.documentElement.append(fileInput)

document.getElementById("filepicker").addEventListener(
  "change",
  async (event) => {
    const files = event.target.files
    const locales = {}
    const localeFiles = Object.values(files)
      .filter(f => f.name == 'messages.json')
      .filter(f => f.type == 'application/json')

    for (const localeFile of localeFiles) {
      const localeCode = localeFile.webkitRelativePath
        .replace('_locales/', '')
        .replace('/messages.json', '')
      const fileText = await localeFile.text()
      const localeJson = JSON.parse(fileText)
      if (localeJson.storeDesc) {
        locales[localeCode] = localeJson.storeDesc.message
      } else {
        console.error(`[${localeCode}] - no store desc for this locale: ${fileText}`)
      }
    }

    console.log("all locales:", locales)
    await uploadLocales(locales)
  },
  false,
)

function sleep(time) {
  return new Promise((resolve) => setTimeout(resolve, time))
}

async function uploadLocales(locales) {
  const dropdown = document.evaluate(
    "//h3[text()='Current editing language']/../../div[2]//div[@jsshadow]/div/div",
    document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
  ).singleNodeValue

  for (const entry of Object.entries(locales)) {
    let code = entry[0].replace('_', '-')
    const description = entry[1]

    // CWS uses 'iw' instead of 'he' for Hebrew
    if (code === 'he') {
      code = 'iw'
    }

    console.log('upload locale:', code)
    dropdown.click()

    try {
      [...document.evaluate(
        "//ul[@aria-label='Language']",
        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
      ).singleNodeValue.children]
        .filter(e => e.tagName == 'LI')
        .filter(e => e.getAttribute('data-value') == code)[0]
        .click()
    } catch (e) {
      console.error("cant find locale with code - ", code)
      continue
    }
    await sleep(ANIMATION_TIMEOUT)

    const textarea = document.evaluate(
      "//textarea[@maxlength='16000']",
      document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null
    ).singleNodeValue
    textarea.dispatchEvent(new Event("focus"))
    textarea.value = description
    textarea.dispatchEvent(new Event('input', { bubbles: true }))
    await sleep(ANIMATION_TIMEOUT)
  }
}
