venv/bin/activate:
	python3 -m venv venv
	. venv/bin/activate; pip install -Ur requirements.txt
	. venv/bin/activate; pip install -Ur requirements-dev.txt

deps: venv/bin/activate
	. venv/bin/activate; pip install -Ur requirements.txt
	. venv/bin/activate; pip install -Ur requirements-dev.txt

# bring up the compose stack with snipe-it
dev: venv/bin/activate
	docker-compose up -d

# resets to a basic setup with the admin user set to admin:password
setup-db:
	docker-compose stop snipe-it
	docker-compose exec mysql bash -c "mysql -u root -pYOUR_SUPER_SECRET_PASSWORD -e 'DROP DATABASE IF EXISTS snipeit;'"
	docker-compose exec mysql bash -c "mysql -u root -pYOUR_SUPER_SECRET_PASSWORD -e 'CREATE DATABASE snipeit;'"
	docker-compose exec mysql bash -c "mysql -u root -pYOUR_SUPER_SECRET_PASSWORD < /db.dump"
	docker-compose start snipe-it

# warning! includes volumes
down:
	docker-compose down --volumes

clean:
	docker-compose down --volumes
	rm -rf venv

clean-venv:
	rm -rf venv
