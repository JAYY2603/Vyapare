(function (global) {
  let zxingLoadPromise = null;

  function loadZxingLibrary() {
    if (global.ZXing && global.ZXing.BrowserMultiFormatReader) {
      return Promise.resolve(global.ZXing);
    }

    if (zxingLoadPromise) {
      return zxingLoadPromise;
    }

    zxingLoadPromise = new Promise(function (resolve, reject) {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js";
      script.async = true;
      script.onload = function () {
        if (global.ZXing && global.ZXing.BrowserMultiFormatReader) {
          resolve(global.ZXing);
        } else {
          reject(new Error("ZXing loaded but reader is unavailable."));
        }
      };
      script.onerror = function () {
        reject(new Error("Failed to load ZXing library."));
      };
      document.head.appendChild(script);
    });

    return zxingLoadPromise;
  }

  function createScanner(config) {
    const videoEl = config.videoElement;
    const statusEl = config.statusElement;
    const onDetected = config.onDetected;

    let stream = null;
    let scanner = null;
    let zxingReader = null;
    let rafId = null;
    let lastDetectedCode = "";
    let lastDetectedAt = 0;
    let usingZxing = false;

    function setStatus(message, isError) {
      if (!statusEl) {
        return;
      }

      statusEl.textContent = message;
      statusEl.classList.toggle("field-error", Boolean(isError));
    }

    function enableControls(isRunning) {
      return isRunning;
    }

    function stop() {
      if (rafId) {
        global.cancelAnimationFrame(rafId);
        rafId = null;
      }

      if (zxingReader) {
        try {
          zxingReader.reset();
        } catch (error) {
          // Ignore reset errors from stale readers.
        }
        zxingReader = null;
      }

      usingZxing = false;

      if (stream) {
        stream.getTracks().forEach(function (track) {
          track.stop();
        });
        stream = null;
      }

      if (videoEl) {
        videoEl.srcObject = null;
      }

      enableControls(false);
      setStatus("Camera stopped.", false);
    }

    async function scanFrame() {
      if (usingZxing) {
        return;
      }

      if (!scanner || !videoEl || videoEl.readyState < 2) {
        rafId = global.requestAnimationFrame(scanFrame);
        return;
      }

      try {
        const barcodes = await scanner.detect(videoEl);
        if (barcodes && barcodes.length) {
          const rawCode = (barcodes[0].rawValue || "").trim();
          const now = Date.now();

          if (rawCode && (rawCode !== lastDetectedCode || now - lastDetectedAt > 1500)) {
            lastDetectedCode = rawCode;
            lastDetectedAt = now;
            setStatus("Barcode detected: " + rawCode, false);
            if (typeof onDetected === "function") {
              onDetected(rawCode);
            }
          }
        }
      } catch (error) {
        setStatus("Barcode detection failed.", true);
      }

      rafId = global.requestAnimationFrame(scanFrame);
    }

    async function startWithZxing() {
      try {
        const ZXing = await loadZxingLibrary();
        zxingReader = new ZXing.BrowserMultiFormatReader();
        usingZxing = true;

        enableControls(true);
        setStatus("Scanning with fallback scanner...", false);

        await zxingReader.decodeFromVideoDevice(
          null,
          videoEl,
          function (result, error) {
            if (!result) {
              return;
            }

            const rawCode = String(result.getText ? result.getText() : result.text || "").trim();
            const now = Date.now();

            if (rawCode && (rawCode !== lastDetectedCode || now - lastDetectedAt > 1500)) {
              lastDetectedCode = rawCode;
              lastDetectedAt = now;
              setStatus("Barcode detected: " + rawCode, false);
              if (typeof onDetected === "function") {
                onDetected(rawCode);
              }
            }
          },
        );
      } catch (error) {
        setStatus("Scanner fallback failed to start.", true);
        stop();
      }
    }

    async function start() {
      if (!global.isSecureContext) {
        setStatus("Camera requires HTTPS or localhost.", true);
        return;
      }

      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: {
              ideal: "environment",
            },
          },
          audio: false,
        });

        videoEl.srcObject = stream;
        await videoEl.play();

        if ("BarcodeDetector" in global) {
          scanner = new global.BarcodeDetector({
            formats: [
              "code_128",
              "ean_13",
              "ean_8",
              "upc_a",
              "upc_e",
              "code_39",
              "codabar",
            ],
          });

          enableControls(true);
          setStatus("Scanning... point the barcode at the camera.", false);
          rafId = global.requestAnimationFrame(scanFrame);
        } else {
          setStatus("Native detector unavailable, loading fallback scanner...", false);
          await startWithZxing();
        }
      } catch (error) {
        setStatus("Could not start camera. Please check browser camera permissions.", true);
        stop();
      }
    }

    enableControls(false);

    return {
      start: start,
      stop: stop,
      setStatus: setStatus,
    };
  }

  global.DatasetBarcodeScanner = {
    create: createScanner,
  };
})(window);
