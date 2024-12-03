CORE_SIMPLE = ign_simple
CORE_BOOSTED = ign_boosted
SCHEMA_DIR = docker/solr/conf
DATA_DIR = data
QUERIES_DIR = queries
SCRIPTS_DIR = scripts
RESULTS_DIR = results

.PHONY: help down up clean setup-cores index-data index-data-subset query-results-sys1 query-results-sys2 qrels2trec qrels2trec-copy query-plot-sys1 query-plot-sys2 query all-queries

help:
	@echo "Commands:"
	@echo "down       		  : stops all running services"
	@echo "up         		  : starts Solr with both cores"
	@echo "clean              : removes all cores"
	@echo "setup-cores		  : creates and configures both cores"
	@echo "index-data 		  : indexes data into both cores"
	@echo "index-data-subset  : indexes subset data into both cores"
	@echo "query-results-sys1 : runs queries on simple core"
	@echo "query-results-sys2 : runs queries on boosted core"

down:
	docker-compose down

up:
	docker-compose up -d

clean:
	docker exec -it $$(docker ps -qf "name=solr") solr delete -c $(CORE_SIMPLE) || true
	docker exec -it $$(docker ps -qf "name=solr") solr delete -c $(CORE_BOOSTED) || true
	sleep 2

setup-cores:
	docker exec -it $$(docker ps -qf "name=solr") solr create_core -c $(CORE_SIMPLE) -d /opt/solr/server/solr/configsets/_default
	docker exec -it $$(docker ps -qf "name=solr") solr create_core -c $(CORE_BOOSTED) -d /opt/solr/server/solr/configsets/_default
	sleep 2
	curl -X POST -H 'Content-type:application/json' --data-binary @$(SCHEMA_DIR)/simple_schema.json "http://localhost:8983/solr/$(CORE_SIMPLE)/schema"
	curl -X POST -H 'Content-type:application/json' --data-binary @$(SCHEMA_DIR)/boosted_schema.json "http://localhost:8983/solr/$(CORE_BOOSTED)/schema"

index-data:
	curl -X POST -H 'Content-type:application/json' --data-binary "@$(DATA_DIR)/ign_processed.json" "http://localhost:8983/solr/$(CORE_SIMPLE)/update?commit=true"
	curl -X POST -H 'Content-type:application/json' --data-binary "@$(DATA_DIR)/ign_processed.json" "http://localhost:8983/solr/$(CORE_BOOSTED)/update?commit=true"

index-data-subset:
	curl -X POST -H 'Content-type:application/json' --data-binary "@$(DATA_DIR)/ign_subset.json" "http://localhost:8983/solr/$(CORE_SIMPLE)/update?commit=true"
	curl -X POST -H 'Content-type:application/json' --data-binary "@$(DATA_DIR)/ign_subset.json" "http://localhost:8983/solr/$(CORE_BOOSTED)/update?commit=true"

query-results-sys1:
	python3 $(SCRIPTS_DIR)/query_solr.py --query $(QUERIES_DIR)/$(QUERY)/query_sys1.json --uri http://localhost:8983/solr --collection $(CORE_SIMPLE) | python3 $(SCRIPTS_DIR)/solr2trec.py > $(RESULTS_DIR)/$(QUERY)/results_sys1_trec.txt

query-results-sys2:
	python3 $(SCRIPTS_DIR)/query_solr.py --query $(QUERIES_DIR)/$(QUERY)/query_sys2.json --uri http://localhost:8983/solr --collection $(CORE_BOOSTED) | python3 $(SCRIPTS_DIR)/solr2trec.py > $(RESULTS_DIR)/$(QUERY)/results_sys2_trec.txt

qrels2trec:
	cat $(QUERIES_DIR)/$(QUERY)/qrels.txt | python3 $(SCRIPTS_DIR)/qrels2trec.py > $(RESULTS_DIR)/$(QUERY)/qrels_trec.txt

qrels2trec-copy:
	cp $(QUERIES_DIR)/$(QUERY)/qrels.txt $(RESULTS_DIR)/$(QUERY)/qrels_trec.txt

query-plot-sys1:
	cat $(RESULTS_DIR)/$(QUERY)/results_sys1_trec.txt | python3 $(SCRIPTS_DIR)/plot_pr.py --qrels $(RESULTS_DIR)/$(QUERY)/qrels_trec.txt --output $(RESULTS_DIR)/$(QUERY)/prec_rec_sys1.png

query-plot-sys2:
	cat $(RESULTS_DIR)/$(QUERY)/results_sys2_trec.txt | python3 $(SCRIPTS_DIR)/plot_pr.py --qrels $(RESULTS_DIR)/$(QUERY)/qrels_trec.txt --output $(RESULTS_DIR)/$(QUERY)/prec_rec_sys2.png

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