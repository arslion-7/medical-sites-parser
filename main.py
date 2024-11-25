from quart import Quart, jsonify
import schedule
import time
import logging

from class_parsers.aad import AadParser
from class_parsers.agapovmd import AgapovmdParser
from class_parsers.dermatologyadvisor import DermatologyadvisorParser
from class_parsers.dermnetnz import DermnetnzParser
from class_parsers.jamanetwork import JamanetworkParser
from class_parsers.mdedge_pediatric import MdedgePediatricParser
from class_parsers.medicalnewstoday import MedicalnewstodayParser
from class_parsers.medilib import MedilibParser
from class_parsers.medscape import MedscapeParser
from class_parsers.newsmedical import NewsmedicalParser
from class_parsers.onlinelibrary_wiley import OnlinelibraryWileyParser
from class_parsers.pubmed import PubmedParser
from class_parsers.uptodate import UptodateParser
from class_parsers.msdmanuals import MsdmanualsParser
from class_parsers.ncbi_nlm_nih import NcbiNlmNihParser
from db.mongodb_local import test_save_article
from db.mongodb import save_article
from class_parsers.medicaldialogues import MedicaldialoguesParser
from func_parsers.dermatologyadvisor import parse_dermatologyadvisor_site
from func_parsers.healio import parse_heailo_site
from func_parsers.mdedge import parse_mdedge_site
from func_parsers.medicaldialogues import parse_medicaldialogues_site
from func_parsers.medicalnewstoday import parse_medicalnewstoday_site
from func_parsers.medscape import parse_medscape_site
from func_parsers.newsMedical import parse_newsmedical_site
from func_parsers.practicalDermotology import parse_practicaldermotology_site
from helper import Pagination
from indexing import index_articles, index_articles_pdf, index_published_articles

DEBUG = False

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)d')

logger = logging.getLogger(__name__)

# Assuming you have the parse functions already defined

parse_weeks_count = 52 # one year == 52 weeks
save_action = save_article

if DEBUG:
    save_action = test_save_article

medicaldialogues = MedicaldialoguesParser(
    main_url='https://medicaldialogues.in/dermatology/news',
    pagination=Pagination(pagination_format='/page/{page}/', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

dermatologyadvisor = DermatologyadvisorParser(
    main_url='https://www.dermatologyadvisor.com/news/',
    pagination=Pagination(pagination_format='/page/{page}/', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medicalnewstoday = MedicalnewstodayParser(
    main_url='https://www.medicalnewstoday.com/categories/dermatology',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medscape_11732 = MedscapeParser(
    main_url='https://www.medscape.com/index/list_11732',
    pagination=Pagination(pagination_format='_{page}', page_start=0),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medscape_3809 = MedscapeParser( # у старых статей формат даты другой (не учтено)
    main_url='https://www.medscape.com/index/list_3809',
    pagination=Pagination(pagination_format='_{page}', page_start=0),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

mdedge_pediatric = MdedgePediatricParser(
    main_url='https://www.mdedge.com/dermatology/pediatric-dermatology/latest',
    pagination=Pagination(pagination_format='?page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

jamanetwork_jamadermatology = JamanetworkParser(
    main_url='https://jamanetwork.com/journals/jamadermatology',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

aad = AadParser(
    main_url='https://www.aad.org/public/diseases/a-z',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

ncbi_nlm_nih = NcbiNlmNihParser(
    main_url='https://www.ncbi.nlm.nih.gov/books/NBK430685/',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_672 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/672',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_669 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/669',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_676 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/676',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_677 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/677',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_678 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/678',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_679 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/679',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_680 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/680',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_681 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/681',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_682 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/682',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_683 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/683',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_684 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/684',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_685 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/685',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_686 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/686',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

medilib_687 = MedilibParser(
    main_url='https://medilib.ir/UpToDate/687',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_a = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-a.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_b = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-b.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_v = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-v.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_g = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-g.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_d = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-d.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_i = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-i.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_k = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-k.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_l = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-l.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_m = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-m.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_n = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-n.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_o = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-o.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_p = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-p.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_r = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-r.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_s = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-s.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_t = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-t.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_u = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-u.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_f = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-f.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_x = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-x.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_c = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-c.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_ch = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-ch.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_h = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-h.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_w = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-w.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

agapovmd_y = AgapovmdParser(
    main_url='https://agapovmd.ru/dis/skin/index-y.htm',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

dermnetnz = DermnetnzParser(
    main_url='https://dermnetnz.org/topics',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

msdmanuals = MsdmanualsParser(
    main_url='https://www.msdmanuals.com/professional/dermatologic-disorders',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)

uptodate = UptodateParser(
    main_url='https://www.uptodate.com/contents/whats-new-in-dermatology',
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action)


newsmedical = NewsmedicalParser(
    main_url='https://www.news-medical.net/condition/Dermatology',
    pagination=Pagination(pagination_format='?page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action
)


# main_url='https://pubmed.ncbi.nlm.nih.gov/?term=dermatology&sort=date',
# main_url='https://pubmed.ncbi.nlm.nih.gov/?term=dermatology&filter=simsearch2.ffrft&filter=years.2022-2024&sort=date&size=10',
pubmed = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=dermatology&filter=simsearch2.ffrft&filter=years.2023-2024&sort=date&size=20',
    pagination=Pagination(pagination_format='&page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
)

# main_url='https://pubmed.ncbi.nlm.nih.gov/?term=pediatric+dermatology&sort=date',
# main_url='https://pubmed.ncbi.nlm.nih.gov/?term=dermatology&filter=simsearch2.ffrft&filter=years.2020-2021&sort=date&size=20',
pubmed_pediatric = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=pediatric+dermatology&filter=simsearch2.ffrft&filter=years.2022-2024&sort=date&size=10',
    pagination=Pagination(pagination_format='&page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
    subcategory='Детская дерматология'
)

pubmed_trichology = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=trichology&filter=simsearch2.ffrft&filter=years.2019-2024&sort=date&size=20',
    pagination=Pagination(pagination_format='&page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
    subcategory='Трихология'
)

pubmed_neonatal_dermatology = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=neonatal+dermatology&filter=simsearch2.ffrft&filter=years.2019-2024&sort=date&size=20',
    pagination=Pagination(pagination_format='&page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
    subcategory='Неонатальная дерматология'
)

pubmed_dermatovenerology = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=dermatovenerology&filter=simsearch2.ffrft&filter=years.2019-2024&sort=date&size=20',
    pagination=Pagination(pagination_format='&page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
    subcategory='Дерматовенерология'
)

pubmed_dermato_oncology = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=dermato-oncology&filter=simsearch2.ffrft&filter=years.2019-2024&sort=date&size=20',
    pagination=Pagination(pagination_format='&page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
    subcategory='Дерматоонкология'
)

pubmed_seborrheic_dermatitis = PubmedParser(
    main_url='https://pubmed.ncbi.nlm.nih.gov/?term=seborrheic+dermatitis&filter=simsearch2.ffrft&filter=years.2019-2024&sort=date&size=20',
    pagination=Pagination(pagination_format='&page={page}', page_start=1),
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles',
    subcategory='Себорейный дерматит'
)

# main_url='https://onlinelibrary.wiley.com/action/doSearch?SeriesKey=15251470&sortBy=Earliest&',
onlinelibrary_wiley = OnlinelibraryWileyParser(
    main_url='https://www.espd.info/wiley-token',
    # pagination=Pagination(pagination_format='startPage={page}&pageSize=20', page_start=0),
    pagination=None,
    parse_weeks_count=parse_weeks_count,
    save_action=save_action,
    category='articles'
)

    # disabled functions
    # parse_newsmedical_site,

parsers = [
    # ready to parse 
    # parse_practicaldermotology_site, 
    # parse_mdedge_site,
    # parse_heailo_site,
    # medicaldialogues.main,
    # dermatologyadvisor.main,
    # medicalnewstoday.main,
    # medscape_11732.main,
    # medscape_3809.main,
    # mdedge_pediatric.main,
    # newsmedical.main,
    # pubmed.main,
    # pubmed_pediatric.main,
    pubmed_trichology.main,
    # pubmed_neonatal_dermatology.main,
    # pubmed_dermatovenerology.main,
    # pubmed_dermato_oncology.main,
    # pubmed_seborrheic_dermatitis.main,
    # onlinelibrary_wiley.main,
    
    # on time parse
    
    # uptodate.main,
    # msdmanuals.main,
    # dermnetnz.main,
    # aad.main,
    # ncbi_nlm_nih.main,
    # agapovmd_a.main,
    # agapovmd_b.main,
    # agapovmd_v.main,
    # agapovmd_g.main,
    # agapovmd_d.main,
    # agapovmd_i.main,
    # agapovmd_k.main,
    # agapovmd_l.main,
    # agapovmd_m.main,
    # agapovmd_n.main,
    # agapovmd_o.main,
    # agapovmd_p.main,
    # agapovmd_r.main,
    # agapovmd_s.main,
    # agapovmd_t.main,
    # agapovmd_u.main,
    # agapovmd_f.main,
    # agapovmd_x.main,
    # agapovmd_c.main,
    # agapovmd_ch.main,
    # agapovmd_h.main,
    # agapovmd_w.main,
    # agapovmd_y.main,
    # medilib_672.main,
    # medilib_669.main,
    # medilib_676.main,
    # medilib_677.main,
    # medilib_678.main,
    # medilib_679.main,
    # medilib_680.main,
    # medilib_681.main,
    # medilib_682.main,
    # medilib_683.main,
    # medilib_684.main,
    # medilib_685.main,
    # medilib_686.main,
    # medilib_687.main,

    # not ready for parse yet
    # jamanetwork_jamadermatology.main,
]

app = Quart(__name__)

def run_parsing_and_indexing():
    try:
        run_parsers()
        logger.info("successfully parsed sites")
        index_articles()
        logger.info("successfully indexed new articles")
        index_articles_pdf()
        logger.info("successfully indexed PDFs of articles")
        index_published_articles()
        logger.info("successfully indexed Translation of published articles")
    except Exception as e:
        logger.error(f"something whent wrong: {str(e)}")

def run_parsers():
    results = []
    for parser in parsers:
        parser()
        results.append(f"parsed {parser.__name__}")

    logger.info("finished running parsers")
    return results

@app.route('/run-parsers', methods=['POST'])
async def run_parsers_endpoint():
    results = run_parsers()
    return jsonify(results)

if __name__ == '__main__':
    # app.run("0.0.0.0", int(os.getenv('PORT', 5001)))
    # run_parsing_and_indexing()
    run_parsers()
    # schedule.every().day.at("07:00").do(run_parsers)
    # schedule.every(3).hours.do(run_parsing_and_indexing)
    # # schedule.every(10).minutes.do(run_parsers)
    # if DEBUG:
    #     print('heere')
    #     logger.info("starting local test")
    #     run_parsers()
    # else:    
    # # Infinite loop to keep the script running
    #     logger.info("starting scheduler")
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(60) 



