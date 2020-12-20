from datetime import datetime
import elasticsearch_dsl as es

es.connections.create_connection(hosts=['localhost'], timeout=20)


class EsPhenotype(es.Document):
    timestamp = es.Date(required=True, default_timezone="UTC")
    pool_id = es.Keyword(required=True)
    pool_generation = es.Long(required=True)
    pool_size = es.Integer(required=True)

    rank = es.Integer(required=True)
    fitness = es.Float(required=True)
    phenotype = es.Keyword(required=True)
    phenotype_id = es.Keyword(required=True)
    name = es.Keyword()
    param = es.Object(dynamic=True)
    param_hash = es.Keyword(required=True)
    stats = es.Object(dynamic=True)

    class Index:
        name = "game-evo-pool"

    def save(self, **kwargs):
        self.timestamp = datetime.now().astimezone()
        super().save(**kwargs)


def test_query():
    s = EsPhenotype.search()
    s = s.query("match", phenotype="PolyPhenotype")

    #s.aggs.bucket("timeline", "date_histogram", calendar_interval="1h", field="timestamp").metric("fitness", "avg", field="fitness")
    s.aggs.bucket("param_hash", "terms", field="param_hash", size=20, order={"fitness": "desc"})\
        .metric("fitness", "avg", field="fitness")\
        .metric("top", "top_hits", size=1)
    #s = s.sort("-fitness")
    #s.query("query_string", query="fitness > -1000")

    s = s[0:2]
    response = s.execute()
    for hit in response:
        print(hit.param_hash, hit.fitness, hit.name)
    #print(r.aggs.timeline.to_dict())
    print(response.aggs.param_hash.to_dict())
    for tag in response.aggs.param_hash.buckets:
        print(tag.to_dict())

# test_query()