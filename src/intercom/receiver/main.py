import threading

import uvicorn
from gi.repository import GLib

from intercom.receiver.api.app import create_app
from intercom.receiver.audio.gst_pipeline import GstAudioPipeline
from intercom.receiver.audio.receiver import Receiver
from intercom.shared.config import ReceiverConfig
from intercom.shared.exceptions import IntercomError
from intercom.shared.logger import logger


def main() -> None:
    config = ReceiverConfig.from_yaml()

    pipeline = GstAudioPipeline(config)
    receiver = Receiver(pipeline)

    try:
        receiver.start()
    except IntercomError:
        logger.exception("Receiver failed to start")
        raise SystemExit(1)

    logger.info("Receiver started")

    # The GStreamer bus signal watch only fires while the GLib main context
    # is pumped; run it on a background thread since uvicorn owns the main
    # thread's asyncio loop.
    glib_loop = GLib.MainLoop()
    glib_thread = threading.Thread(target=glib_loop.run, name="gst-bus-loop", daemon=True)
    glib_thread.start()

    app = create_app(receiver, config)

    ssl_kwargs = {}
    if config.api_ssl_certfile and config.api_ssl_keyfile:
        ssl_kwargs = {
            "ssl_certfile": str(config.api_ssl_certfile),
            "ssl_keyfile": str(config.api_ssl_keyfile),
        }
    else:
        logger.warning(
            "No SSL certificate configured; browsers will refuse microphone "
            "access on the mobile page over plain HTTP"
        )

    server = uvicorn.Server(
        uvicorn.Config(app, host="0.0.0.0", port=config.api_port, log_level="info", **ssl_kwargs)
    )

    try:
        server.run()
    finally:
        glib_loop.quit()
        receiver.stop()
        logger.info("Receiver stopped")


if __name__ == "__main__":
    main()
