



from class_parsers.pubmed_doi.academic_oup import AcademicOupParser
from class_parsers.pubmed_doi.cureus import CureusParser
from class_parsers.pubmed_doi.dovepress import DovepressParser
from class_parsers.pubmed_doi.dpcj import DpcjParser
from class_parsers.pubmed_doi.frontiersin_org import FrontiersinOrgParser
from class_parsers.pubmed_doi.ijdvl import IjdvlParser
from class_parsers.pubmed_doi.journals_lww import JournalsLwwParser
from class_parsers.pubmed_doi.mdpi import MdpiParser

# running by
# python3 -m draft.test_sub

# dpcj = IjdvlParser(url='https://ijdvl.com/ijdvl-the-success-story/', main_url='', is_selenium=True)

# result = dpcj.main()

# print('authors', result['authors'])
# print('body', result['content'])



# dpcj = DpcjParser(url='https://dpcj.org/index.php/dpc/article/view/4240', main_url='', is_selenium=True)

# result = dpcj.main()

# print('refs', result['references'])



# j = DovepressParser(url='https://www.dovepress.com/rare-case-report-of-primary-active-pulmonary-tuberculosis-during-ixeki-peer-reviewed-fulltext-article-CCID',
#                   main_url='', is_selenium=True)
# j = j.main()

# print('jjjj', j['content'])


# j = JournalsLwwParser(url='https://journals.lww.com/ijwd/fulltext/2024/10000/the_reporting_of_social_determinants_of_health_in.13.aspx',
#                   main_url='', is_selenium=True)
# j = j.main()

# print('jjjj', j['content'])

# with open('draft/j_result.txt', 'w') as f:
#   f.write(str(j))
# f.close()


cureus = CureusParser(url='https://www.cureus.com/articles/276123-beyond-the-usual-suspects-unraveling-spleen-mastocytosis-in-hypersplenism-differential-diagnosis',
                  main_url='', is_selenium=True)
c = cureus.main()

with open('draft/cureus.md', 'w') as f:
  f.write(c['content'])

f.close()





# with open('draft/cureus_result.txt', 'w') as f:
#   f.write(str(c))
# f.close()


# frontiersin = FrontiersinOrgParser(url='https://www.frontiersin.org/journals/medicine/articles/10.3389/fmed.2024.1433153/full',
#                   main_url='')

# result = frontiersin.main()

# with open('draft/frontiersin.txt', 'w') as f:
#   f.write(str(result['content']))
# f.close()


# mdpi = MdpiParser(url='https://www.mdpi.com/1999-4923/16/7/876',
#                   main_url='https://www.mdpi.com', is_selenium=True)
# result = mdpi.main()

# with open('draft/result_content.md', 'w') as f:
#   f.write(result['content'])

# f.close()


# academic_oup = AcademicOupParser(url='https://academic.oup.com/ofid/article/11/8/ofae388/7710506?login=false',
#                                  main_url='https://academic.oup.com', is_selenium=True)
# ao = academic_oup.main()


# print('ao', ao['references'])

