STREAM_URI=rtsp://username:password@10.0.0.10/live
PI_IP_ADDRESS=10.0.0.5

.PHONY: run
run:
	@echo "Starting Doorbell"
	@. env/bin/activate && export STREAM_URI=$(STREAM_URI) && cd src && python app.py

.PHONY: install
install:
	@cd scripts && bash install_pi.sh

.PHONY: copy
copy:
	@rsync -a --exclude env ./ pi@$(PI_IP_ADDRESS):/home/pi/facial_recognition_doorbell/

.PHONY: shell
shell:
	@ssh pi@$(PI_IP_ADDRESS)
