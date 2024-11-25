
import logging
from class_parsers.onlinelibrary_wiley import OnlinelibraryWileyParser
from class_parsers.pubmed import PubmedParser
from class_parsers.pubmed_doi.aafp_org import AafpOrgParser
from db.mongodb import save_article
from db.mongodb_local import test_save_article


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')

DEBUG = False

save_action = save_article
parse_weeks_count = 120 # don't edit it (because inside has check for date of publish)

if DEBUG:
    save_action = test_save_article

aafp_org_1 = AafpOrgParser(
    url='https://www.aafp.org/pubs/afp/issues/2018/0101/p38.html',
    main_url='https://www.aafp.org',
    is_selenium=True,
)

onlinelibrary_wiley = OnlinelibraryWileyParser(
    main_url='https://www.espd.info/wiley-token',
    # pagination=Pagination(pagination_format='startPage={page}&pageSize=20', page_start=0),
    certain_article_urls=[
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15814',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15692',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15674',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15665',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15657',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15253'
        # 'https://onlinelibrary.wiley.com/doi/10.1002/clt2.70002',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15805',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15768',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15781',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15782',


        # 'https://onlinelibrary.wiley.com/doi/10.1155/2024/9572303',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15742',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15379'
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15010',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15372',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15266',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15753',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15777',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15651',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15578',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15472',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15394',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15114',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15026',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15223',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15720',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15771',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15761',
     
    ],
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
)


        # 'https://www.pubmed.ncbi.nlm.nih.gov/35265550/', # +
pubmed = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=dermatology&sort=date',
    certain_article_urls=[
        'https://www.pubmed.ncbi.nlm.nih.gov/39170089/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39170091/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39170085/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39170085/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39170087/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507133/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507268/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507180/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507179/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507375/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507409/',

        # 'https://pubmed.ncbi.nlm.nih.gov/39507768/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507766/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507767/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507751/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39507636/',


        # 'https://pubmed.ncbi.nlm.nih.gov/39508035/',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15805',
        # 'https://pubmed.ncbi.nlm.nih.gov/39483123/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39483589/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39483464/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39484071/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39485847/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39453829/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39455575/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39455600/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456176/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456231/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456243/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456251/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456425/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456430/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456587/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456614/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456844/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39456853/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457071/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457108/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457218/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457256/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457361/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457482/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457500/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457540/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457721/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39457851/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458148/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458184/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458225/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458260/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458319/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458596/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458602/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458612/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458624/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458943/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39458983/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459015/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459016/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459387/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459395/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459397/',




        # 'https://pubmed.ncbi.nlm.nih.gov/39459406/',

        # 'https://pubmed.ncbi.nlm.nih.gov/39459523/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459488/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459536/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459533/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459585/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459597/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39459952/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39460328/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39460324/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39460334/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39360229/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39359912/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39359916/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39359925/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361839/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361840/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361841/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361842/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361843/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361845/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361846/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361847/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361848/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361849/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361850/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361851/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361852/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361853/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361854/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361856/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361857/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361858/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361859/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361860/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361861/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361865/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361864/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361863/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361862/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361866/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39361855/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/38910684/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/38921259/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/38931395/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39184770/',
        # 'https://pubmed.ncbi.nlm.nih.gov/39152862/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39125589/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39124838/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39006495/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/39126011/',
        # "https://www.pubmed.ncbi.nlm.nih.gov/39125287/",
        # "https://www.pubmed.ncbi.nlm.nih.gov/39125519/",
        # "https://www.pubmed.ncbi.nlm.nih.gov/39125589/",
        # "https://www.pubmed.ncbi.nlm.nih.gov/39125548/",
        # "https://www.pubmed.ncbi.nlm.nih.gov/39124838/",
        # "https://www.pubmed.ncbi.nlm.nih.gov/39125541/",
        # "https://www.pubmed.ncbi.nlm.nih.gov/39125514/",

    ],
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles'
)

parsers = [
    pubmed.main,
    # onlinelibrary_wiley.main,
    # aafp_org_1.main,
]

def run_parsers():
    results = []
    print('parse_certain_urls started')
    for parser in parsers:
        parser()
        results.append(f"parsed {parser.__name__}")

    logger.info("finished running parsers")
    return results


if __name__ == '__main__':
    logger.info('parsing started')
    run_parsers()
    # app.run("0.0.0.0", int(os.getenv('PORT', 5001)))
    # run_parsing_and_indexing()
