# foe-bot

## signing

- open the city with browser debugger
- find the url of the java script source of the game, `https://foede.innogamescdn.com//cache/ForgeHX-5ac04db0.js` for instance and download that script
- search for `Signature` in the file and you will find a method like 
    ```
  _generateRequestPayloadSignature: function (a) {
          return Ea.substr(IQ.encode(this._hash + "RrTNMxkHHQFE2otQVSTZMXcq2gy2zpY5hVG/YyIuDqwV8ZYbYrPnUjEK9R8mqNf2AyY7Zjt5KaRR/BsG2IUxmQ==" + a), 0, 10)
    ```
- the signature is are the first 10 character of the md5 hash of `request body` + `RrTNMxkHHQFE2otQVSTZMXcq2gy2zpY5hVG/YyIuDqwV8ZYbYrPnUjEK9R8mqNf2AyY7Zjt5KaRR/BsG2IUxmQ==` + `playerId`

