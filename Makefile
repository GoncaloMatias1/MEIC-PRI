.PHONY: help down up setup-cores index-data

help:
	@echo "Commands:"
	@echo "down       : stops all running services"
	@echo "up         : starts Solr with both cores"
	@echo "setup-cores: creates and configures both cores"
	@echo "index-data : indexes data into both cores"

down:
	docker-compose down

up:
	docker-compose up -d

setup-cores:
	docker exec -it $$(docker ps -qf "name=solr") solr create_core -c ign_simple
	docker exec -it $$(docker ps -qf "name=solr") solr create_core -c ign_advanced
	curl -X POST -H 'Content-type:application/json' --data-binary @docker/solr/conf/simple_schema.json "http://localhost:8983/solr/ign_simple/schema"
	curl -X POST -H 'Content-type:application/json' --data-binary @docker/solr/conf/advanced_schema.json "http://localhost:8983/solr/ign_advanced/schema"

index-data:
	curl -X POST -H 'Content-type:application/json' --data-binary "@csv_to_json/ign_processed.json" "http://localhost:8983/solr/ign_simple/update?commit=true"
	curl -X POST -H 'Content-type:application/json' --data-binary "@csv_to_json/ign_processed.json" "http://localhost:8983/solr/ign_advanced/update?commit=true"