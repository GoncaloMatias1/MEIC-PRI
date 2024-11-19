.PHONY: help down up setup-cores index-data index-data-subset query-results-sys1 query-results-sys2 qrels2trec qrels2trec-copy query-plot-sys1 query-plot-sys2 query all-queries

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
	curl -X POST -H 'Content-type:application/json' --data-binary @docker/solr/conf/simple_schema.json "http://localhost:8983/solr/ign_simple/schema"

index-data:
	curl -X POST -H 'Content-type:application/json' --data-binary "@csv_to_json/ign_processed.json" "http://localhost:8983/solr/ign_simple/update?commit=true"

index-data-subset:
	curl -X POST -H 'Content-type:application/json' --data-binary "@csv_to_json/ign_subset.json" "http://localhost:8983/solr/ign_simple/update?commit=true"


query-results-sys1:
	python3 ./scripts/query_solr.py --query config/$(QUERY)/query_sys1.json --uri http://localhost:8983/solr --collection ign_simple | python3 ./scripts/solr2trec.py > results/$(QUERY)/results_sys1_trec.txt

query-results-sys2:
	python3 ./scripts/query_solr.py --query config/$(QUERY)/query_sys2.json --uri http://localhost:8983/solr --collection ign_simple | python3 ./scripts/solr2trec.py > results/$(QUERY)/results_sys2_trec.txt

qrels2trec:
	cat config/$(QUERY)/qrels.txt | python3 ./scripts/qrels2trec.py > results/$(QUERY)/qrels_trec.txt

qrels2trec-copy:
	cp config/$(QUERY)/qrels.txt results/$(QUERY)/qrels_trec.txt

query-plot-sys1:
	cat results/$(QUERY)/results_sys1_trec.txt | python3 ./scripts/plot_pr.py --qrels results/$(QUERY)/qrels_trec.txt --output results/$(QUERY)/prec_rec_sys1.png

query-plot-sys2:
	cat results/$(QUERY)/results_sys2_trec.txt | python3 ./scripts/plot_pr.py --qrels results/$(QUERY)/qrels_trec.txt --output results/$(QUERY)/prec_rec_sys2.png

query:
	$(MAKE) query-results-sys1 QUERY=$(QUERY)
	$(MAKE) query-results-sys2 QUERY=$(QUERY)
	$(MAKE) qrels2trec-copy QUERY=$(QUERY)
	$(MAKE) query-plot-sys1 QUERY=$(QUERY)
	$(MAKE) query-plot-sys2 QUERY=$(QUERY)

all-queries:
	$(MAKE) query QUERY=controls
	$(MAKE) query QUERY=multiplayer
	$(MAKE) query QUERY=relaxing
	$(MAKE) query QUERY=story_narrative
	$(MAKE) query QUERY=technical
