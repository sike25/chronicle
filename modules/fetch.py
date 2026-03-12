from utils.log import setup_logging
from modules.search import search_data_dump

logger = setup_logging()


# Page size for paginating archivi.ng's search API.
PAGE_SIZE = 100
# Hard cap on total documents regardless of signal.
MAX_DOCUMENTS = 500

def fetch_search_results(query: str, fake=True) -> list:
    """
    Fetches search results from archivi.ng's search API.

    Paginates through results, stopping when:
        - Fewer than SIGNAL_THRESHOLD of a page passes the relevance filter, OR
        - MAX_DOCUMENTS total documents have been collected.

    Args:
        query (str): The search query.
        fake  (bool): If True, returns fake data for local development.

    Returns:
        list: Raw result objects ready to be mapped into Entry shapes in pipeline.py.
    """
    if fake:
        logger.info("fetch_results: returning fake data.")
        return _fetch_fake()

    logger.info(f"fetch_results: fetching live results for query '{query}'.")
    return _fetch_from_vertex(query=query)


def _fetch_from_vertex(query: str):
    collected = []
    pager = search_data_dump(search_query=query, fake=False)

    for result in pager:
        if len(collected) >= MAX_DOCUMENTS or result.rank_signals.semantic_similarity_score == 0.0:
            break
        collected.append(result)
    return collected


# ── Live fetcher ──────────────────────────────────────────────────────────────
def _fetch_live(query: str) -> list:
    """
    Paginates through archivi.ng's search API until signal dries up.

    TODO: implement once archivi.ng's search API spec is available.
          Expected pagination params: ?q=query&from=0&size=20
          Expected response shape:
            {
              "total": 1200,
              "hits": [
                {
                  "_id": "...",
                  "_score": 0.87,
                  "_source": { ... }
                }
              ]
            }
    """
    raise NotImplementedError(
        "Live fetcher not yet implemented. "
        "Waiting on archivi.ng search API spec. Use fake=True for local development."
    )

    # stub for when the spec arrives ........................................
    # import requests
    #
    # SEARCH_API_URL = "https://archivi.ng/api/search"
    # all_results = []
    # page = 0
    #
    # while len(all_results) < MAX_DOCUMENTS:
    #     response = requests.get(SEARCH_API_URL, params={
    #         "q":    query,
    #         "from": page * PAGE_SIZE,
    #         "size": PAGE_SIZE,
    #     })
    #     response.raise_for_status()
    #     data = response.json()
    #     hits = data.get("hits", [])
    #
    #     if not hits:
    #         logger.info("fetch: no more results. Stopping.")
    #         break
    #
    #     # check signal — how many hits on this page pass the relevance threshold
    #     passing = [h for h in hits if h["_score"] >= 0.6]
    #     signal  = len(passing) / len(hits)
    #     logger.debug(f"fetch: page {page} — {len(passing)}/{len(hits)} hits pass filter (signal={signal:.2f})")
    #
    #     all_results.extend(hits)
    #
    #     if signal < SIGNAL_THRESHOLD:
    #         logger.info(f"fetch: signal dropped below {SIGNAL_THRESHOLD}. Stopping.")
    #         break
    #
    #     page += 1
    #
    # logger.info(f"fetch: collected {len(all_results)} results across {page + 1} pages.")
    # return all_results


# ── Fake fetcher ──────────────────────────────────────────────────────────────

class _FakeDocument:
    def __init__(self, id, struct_data):
        self.id          = id
        self.struct_data = struct_data

class _RankSignals:
    def __init__(self):
        self.semantic_similarity_score = 1.0

class _FakeResult:
    def __init__(self, document):
        self.document     = document
        self.rank_signals = _RankSignals()


def _fetch_fake() -> list:
    """
    Returns fake search results for local development.
    10 years of Nigerian election crisis and violence data (2014–2023).
    """
    fake_data = [
        # 2014
        {
            "id": "fake_2014_001",
            "summary": "Violence erupted in Rivers State during gubernatorial elections as political thugs clashed with security forces. At least 12 people were killed in ballot box snatching incidents across several local government areas. INEC officials were forced to flee polling units as armed groups took control.",
            "extract": "Rivers Election Turns Bloody\n\nThe gubernatorial election in Rivers State descended into chaos yesterday as armed political thugs stormed polling units in Obio-Akpor, Port Harcourt City, and Ikwerre local government areas. Witnesses reported that masked gunmen arrived in convoys, firing shots into the air before snatching ballot boxes. Security personnel were overwhelmed as the violence spread. INEC officials abandoned several polling units, leaving materials unguarded. The state police command confirmed 12 deaths and over 30 injuries. Opposition parties have called for the cancellation of results from affected areas.",
            "filename": "2014/April 2014/Vanguard April 12_2014_Pg 1.tif",
            "keywords": "Rivers State, gubernatorial election, political thugs, ballot box snatching, INEC, election violence",
            "image_path": "2014/April 2014/Vanguard April 12_2014_Pg 1.jpeg",
            "topics": "Ballot box snatching, Political thuggery, INEC officials threatened, Gun violence, Election cancellation calls",
            "publication": "Vanguard",
            "publication_date": "2014/04/12",
            "page": "1",
            "tags": "breaking news, rivers state"
        },
        {
            "id": "fake_2014_002",
            "summary": "Boko Haram insurgents attacked multiple polling stations in Borno State, killing election workers and voters. The terrorist group had threatened to disrupt elections in the Northeast. Thousands of internally displaced persons were unable to vote due to security concerns.",
            "extract": "Boko Haram Disrupts Borno Elections\n\nTerrorist attacks by Boko Haram militants left at least 25 people dead across Borno State on election day. The insurgents targeted polling units in Maiduguri, Biu, and Gwoza, burning election materials and killing INEC staff. Security forces engaged the attackers in several locations, but many voters fled before casting their ballots. The attacks came despite heavy military presence in the state. Voter turnout in the Northeast was significantly lower than the national average due to security fears. Human rights groups condemned the violence and called for better protection of democratic processes.",
            "filename": "2014/March 2014/Daily Trust March 29_2014_Pg 2.tif",
            "keywords": "Boko Haram, Borno State, election attacks, INEC workers killed, voter intimidation, Northeast insecurity",
            "image_path": "2014/March 2014/Daily Trust March 29_2014_Pg 2.jpeg",
            "topics": "Terrorist attacks, Election workers killed, Voter suppression, Military deployment, IDP voting rights",
            "publication": "Daily Trust",
            "publication_date": "2014/03/29",
            "page": "2",
            "tags": "terrorism, northeast"
        },
        # 2015
        {
            "id": "fake_2015_001",
            "summary": "Post-election violence broke out in Kaduna State following the gubernatorial election results announcement. Ethnic and religious tensions escalated into deadly clashes between supporters of rival candidates. The military imposed a curfew as the death toll reached 45.",
            "extract": "Kaduna Imposes Curfew After Election Violence\n\nKaduna State descended into chaos as ethnic and religious violence erupted following the announcement of gubernatorial election results. Clashes between supporters of the APC and PDP candidates left at least 45 people dead and hundreds injured. Entire neighborhoods in Kaduna metropolis were set ablaze as mobs attacked residents based on ethnic and religious identity. The state government imposed a 24-hour curfew and deployed soldiers to restore order. Churches and mosques in southern Kaduna were reportedly attacked. Human rights organizations warned of potential genocide if the violence is not contained urgently.",
            "filename": "2015/April 2015/The Guardian April 14_2015_Pg 1.tif",
            "keywords": "Kaduna State, post-election violence, ethnic clashes, religious tension, curfew, military deployment",
            "image_path": "2015/April 2015/The Guardian April 14_2015_Pg 1.jpeg",
            "topics": "Ethnic violence, Religious clashes, Curfew imposed, Military intervention, Arson attacks",
            "publication": "The Guardian",
            "publication_date": "2015/04/14",
            "page": "1",
            "tags": "crisis, kaduna"
        },
        {
            "id": "fake_2015_002",
            "summary": "The presidential election faced massive logistical failures as card readers malfunctioned across the country. INEC postponed elections in several states due to violence and insecurity. Opposition parties accused the ruling party of deliberate sabotage to suppress voter turnout in certain regions.",
            "extract": "Card Reader Failure Mars Presidential Poll\n\nNigeria's presidential election was plagued by widespread card reader malfunctions that left millions of voters frustrated and unable to cast their ballots. In Lagos, Kano, and Rivers states, voting was delayed for hours as INEC officials struggled with the technology. Opposition parties alleged that the failures were deliberate attempts to disenfranchise voters in their strongholds. Violent incidents were reported in Akwa Ibom and Bayelsa states, forcing INEC to suspend voting in some local government areas. Security forces arrested over 200 people for electoral offenses, including vote buying and ballot box snatching. The election was eventually extended to a second day in affected areas.",
            "filename": "2015/March 2015/Punch March 28_2015_Pg 1.tif",
            "keywords": "presidential election, card reader failure, INEC, voter disenfranchisement, election postponement, vote buying",
            "image_path": "2015/March 2015/Punch March 28_2015_Pg 1.jpeg",
            "topics": "Technology failure, Voter disenfranchisement, Election postponement, Vote buying arrests, Logistical chaos",
            "publication": "Punch",
            "publication_date": "2015/03/28",
            "page": "1",
            "tags": "presidential election, inec"
        },
        # 2016
        {
            "id": "fake_2016_001",
            "summary": "Edo State gubernatorial election witnessed unprecedented violence as political thugs attacked voters and INEC officials. The use of firearms and explosives left 18 people dead. International observers condemned the failure of security agencies to protect the electoral process.",
            "extract": "Edo Guber Poll: 18 Dead in Electoral Violence\n\nThe Edo State gubernatorial election turned deadly yesterday as armed thugs unleashed terror on voters across the state. In Benin City, Ekpoma, and Auchi, gunmen attacked polling units, destroying election materials and shooting indiscriminately. Eighteen people were confirmed dead, including three INEC ad-hoc staff members. Security personnel were accused of standing by while thugs operated freely. Several journalists covering the election were assaulted and had their equipment destroyed. The EU Election Observation Mission described the violence as a serious setback for Nigerian democracy. Opposition candidate rejected the results, citing massive irregularities and voter intimidation.",
            "filename": "2016/September 2016/ThisDay September 29_2016_Pg 1.tif",
            "keywords": "Edo State, gubernatorial election, political thugs, INEC staff killed, international observers, electoral violence",
            "image_path": "2016/September 2016/ThisDay September 29_2016_Pg 1.jpeg",
            "topics": "Armed thuggery, INEC workers killed, Journalist attacks, Security failure, International condemnation",
            "publication": "ThisDay",
            "publication_date": "2016/09/29",
            "page": "1",
            "tags": "edo state, violence"
        },
        {
            "id": "fake_2016_002",
            "summary": "Violence flared in Kogi State during local government elections as political rivals clashed. Multiple polling units were set on fire, and election materials were destroyed. The state government accused opposition parties of sponsoring the violence to discredit the electoral process.",
            "extract": "Kogi LG Elections Marred by Arson, Violence\n\nKogi State local government elections were disrupted by widespread violence and arson attacks on polling units. In Lokoja, Okene, and Idah local government areas, thugs set fire to polling centers and destroyed ballot papers. At least 10 people died in clashes between rival political groups. The opposition SDP and PDP accused the ruling APC of using state security apparatus to intimidate voters and rig the election. Electoral materials meant for over 50 polling units were completely destroyed. The Kogi State government denied the allegations, blaming opposition parties for the violence. Civil society organizations called for investigation into the conduct of security agencies.",
            "filename": "2016/December 2016/The Nation December 03_2016_Pg 2.tif",
            "keywords": "Kogi State, local government election, arson, polling units burned, political violence, rigging allegations",
            "image_path": "2016/December 2016/The Nation December 03_2016_Pg 2.jpeg",
            "topics": "Arson attacks, Polling units destroyed, Inter-party violence, Rigging allegations, Security complicity",
            "publication": "The Nation",
            "publication_date": "2016/12/03",
            "page": "2",
            "tags": "kogi state, local government"
        },
        # 2017
        {
            "id": "fake_2017_001",
            "summary": "Anambra State gubernatorial election saw violent clashes between political supporters and security forces. INEC offices were attacked and set ablaze in multiple locations. Separatist groups threatened voters, calling for a boycott of the election.",
            "extract": "Anambra Guber: IPOB Threats, Violence Trail Election\n\nThe Anambra State gubernatorial election was overshadowed by threats from IPOB and violent attacks on electoral infrastructure. In Onitsha, Nnewi, and Awka, suspected separatist members attacked INEC offices, destroying voter registration materials. Several security personnel were killed in ambushes across the state. Despite the threats, voter turnout was moderate in areas where security was maintained. However, many communities in the southern part of the state recorded zero votes due to intimidation. Political parties accused each other of sponsoring the violence. The military declared the exercise largely successful, but civil society groups disputed this claim, citing widespread voter suppression.",
            "filename": "2017/November 2017/Vanguard November 18_2017_Pg 1.tif",
            "keywords": "Anambra State, gubernatorial election, IPOB, separatist violence, INEC offices attacked, voter suppression",
            "image_path": "2017/November 2017/Vanguard November 18_2017_Pg 1.jpeg",
            "topics": "Separatist threats, INEC infrastructure attacks, Security personnel killed, Voter intimidation, Election boycott",
            "publication": "Vanguard",
            "publication_date": "2017/11/18",
            "page": "1",
            "tags": "anambra, ipob"
        },
        {
            "id": "fake_2017_002",
            "summary": "Rivers State rerun elections collapsed into violence as rival cult groups and political thugs took over polling units. The use of military force was criticized as excessive, with allegations of partisanship. At least 22 people were killed in election-related violence.",
            "extract": "Rivers Rerun: Military Accused of Partisanship\n\nThe rerun elections in Rivers State turned bloody as cult groups allegedly sponsored by politicians attacked voters and electoral officials. In Degema, Khana, and Gokana constituencies, armed groups stormed polling units, chasing away INEC staff and voters. The military presence, meant to ensure security, was accused of partisanship by opposition parties. Witnesses claimed soldiers stood by while thugs snatched ballot boxes. At least 22 people were killed, including a serving councilor. International and local observer groups condemned the conduct of the election. The European Union described the polls as falling short of democratic standards. INEC announced plans to investigate the irregularities.",
            "filename": "2017/March 2017/The Guardian March 20_2017_Pg 2.tif",
            "keywords": "Rivers State, rerun election, cult violence, military partisanship, ballot snatching, INEC investigation",
            "image_path": "2017/March 2017/The Guardian March 20_2017_Pg 2.jpeg",
            "topics": "Cult group violence, Military bias allegations, Ballot box snatching, Observer condemnation, Democratic failures",
            "publication": "The Guardian",
            "publication_date": "2017/03/20",
            "page": "2",
            "tags": "rivers state, military"
        },
        # 2018
        {
            "id": "fake_2018_001",
            "summary": "Ekiti State gubernatorial election was characterized by massive vote buying and violent intimidation of opposition supporters. Security agencies arrested several politicians with large sums of money meant for vote buying. Observers reported the worst case of monetization of the electoral process.",
            "extract": "Ekiti Decides: Vote Buying Scandal Rocks Election\n\nThe Ekiti State gubernatorial election exposed the depths of vote buying in Nigerian politics. Across the 16 local government areas, party agents openly distributed cash to voters, with amounts ranging from N3,000 to N10,000 per vote. Security agencies arrested over 50 people, including senior party officials, caught with millions of naira for vote buying. In Ado-Ekiti and Ikere, violence erupted when rival party agents clashed over control of polling units. Opposition parties accused INEC of complicity in the vote buying scheme. International observers described the election as a travesty of democracy. The widespread monetization raised serious questions about the credibility of Nigeria's electoral system.",
            "filename": "2018/July 2018/Punch July 14_2018_Pg 1.tif",
            "keywords": "Ekiti State, gubernatorial election, vote buying, electoral corruption, cash for votes, INEC complicity",
            "image_path": "2018/July 2018/Punch July 14_2018_Pg 1.jpeg",
            "topics": "Vote buying, Electoral corruption, Cash distribution, Party agent arrests, Democratic credibility crisis",
            "publication": "Punch",
            "publication_date": "2018/07/14",
            "page": "1",
            "tags": "ekiti, corruption"
        },
        {
            "id": "fake_2018_002",
            "summary": "Osun State gubernatorial election ended in violence as results were being collated. INEC officials were held hostage by political thugs in Ile-Ife. The election was declared inconclusive, leading to protests and destruction of property across the state.",
            "extract": "Osun Guber Declared Inconclusive Amid Violence\n\nThe Osun State gubernatorial election descended into chaos when INEC declared the results inconclusive due to cancelled votes exceeding the margin of victory. In Ile-Ife, political thugs stormed the collation center and held INEC officials hostage for several hours, demanding favorable results. Supporters of both major parties clashed in Osogbo, Ilesa, and Ede, destroying vehicles and properties. The slim margin between the leading candidates heightened tensions. Both APC and PDP accused each other of planning to manipulate the rerun election. Security was beefed up across the state to prevent further violence. Civil society groups called for transparent conduct of the supplementary election.",
            "filename": "2018/September 2018/ThisDay September 23_2018_Pg 1.tif",
            "keywords": "Osun State, gubernatorial election, inconclusive election, INEC hostage situation, collation center attack, rerun",
            "image_path": "2018/September 2018/ThisDay September 23_2018_Pg 1.jpeg",
            "topics": "Inconclusive election, INEC officials held hostage, Inter-party clashes, Collation center violence, Rerun controversy",
            "publication": "ThisDay",
            "publication_date": "2018/09/23",
            "page": "1",
            "tags": "osun, crisis"
        },
        # 2019
        {
            "id": "fake_2019_001",
            "summary": "The 2019 presidential election recorded at least 39 deaths across multiple states due to election-related violence. Ballot box snatching, voter intimidation, and clashes between political thugs marred the exercise. Opposition parties rejected results in several states, citing widespread irregularities.",
            "extract": "Presidential Poll: 39 Killed in Electoral Violence\n\nNigeria's 2019 presidential election was overshadowed by deadly violence that claimed at least 39 lives across the country. In Rivers, Lagos, Kano, and Delta states, armed thugs disrupted voting, snatched ballot boxes, and attacked INEC officials. The Situation Room, a coalition of civil society organizations, documented over 260 violent incidents during the election. In Rivers State alone, 15 people were killed in election-related violence. Security forces were accused of partisanship and failure to protect voters. The PDP presidential candidate rejected the results, alleging massive rigging, particularly in the North. International observers noted improvements from previous elections but raised concerns about violence and intimidation in several states.",
            "filename": "2019/February 2019/Daily Trust February 24_2019_Pg 1.tif",
            "keywords": "presidential election, electoral violence, ballot box snatching, voter deaths, INEC attacks, election rigging",
            "image_path": "2019/February 2019/Daily Trust February 24_2019_Pg 1.jpeg",
            "topics": "Multiple deaths, Ballot snatching, Voter intimidation, Security failures, Results rejection",
            "publication": "Daily Trust",
            "publication_date": "2019/02/24",
            "page": "1",
            "tags": "presidential, violence"
        },
        {
            "id": "fake_2019_002",
            "summary": "Kano State gubernatorial election was marred by allegations of massive underage voting and violence. Political thugs clashed in multiple local governments. The opposition claimed INEC was complicit in allowing electoral fraud to take place unchecked.",
            "extract": "Kano Guber: Underage Voting, Violence Trail Election\n\nThe Kano State gubernatorial election was characterized by allegations of widespread underage voting and violent clashes between political thugs. In Kano Municipal, Nassarawa, and Dala local government areas, observers documented hundreds of minors casting votes. Political thugs armed with machetes and guns attacked opposition party agents in several polling units. At least 8 people were killed in election-related violence across the state. The PDP candidate rejected the results, presenting photographic evidence of underage voters to INEC. Civil society organizations accused INEC of turning a blind eye to the violations. The controversy reignited debates about voter registration integrity in Northern states.",
            "filename": "2019/March 2019/The Nation March 10_2019_Pg 2.tif",
            "keywords": "Kano State, gubernatorial election, underage voting, political thugs, INEC complicity, electoral fraud",
            "image_path": "2019/March 2019/The Nation March 10_2019_Pg 2.jpeg",
            "topics": "Underage voting, Armed thuggery, Opposition rejection, Photographic evidence, Voter registration fraud",
            "publication": "The Nation",
            "publication_date": "2019/03/10",
            "page": "2",
            "tags": "kano, fraud"
        },
        # 2020
        {
            "id": "fake_2020_001",
            "summary": "Edo State gubernatorial election saw heavy security deployment following threats of violence from political actors. Despite the measures, thugs disrupted voting in several areas. The opposition accused the state government of using security forces to intimidate voters.",
            "extract": "Edo Guber: Security Deployment Fails to Stop Thugs\n\nDespite massive security deployment, the Edo State gubernatorial election was disrupted by political thugs in several local government areas. In Etsako West, Orhionmwon, and Egor, armed groups attacked polling units and destroyed election materials. The police arrested over 40 suspected thugs, but violence continued in isolated areas. Governor Obaseki's camp accused the APC of importing thugs from neighboring states, while the opposition claimed the state government was using security forces for voter suppression. Several journalists were attacked while covering the election. INEC officials in two local governments fled their duty posts due to security threats. The election tribunal later received hundreds of petitions challenging the results.",
            "filename": "2020/September 2020/Vanguard September 19_2020_Pg 1.tif",
            "keywords": "Edo State, gubernatorial election, security deployment, political thugs, voter suppression, journalist attacks",
            "image_path": "2020/September 2020/Vanguard September 19_2020_Pg 1.jpeg",
            "topics": "Heavy security presence, Thug violence, Materials destruction, Journalist harassment, Election petitions",
            "publication": "Vanguard",
            "publication_date": "2020/09/19",
            "page": "1",
            "tags": "edo, security"
        },
        {
            "id": "fake_2020_002",
            "summary": "Ondo State gubernatorial election witnessed vote buying on an industrial scale. Party agents were caught on camera distributing cash to voters. Civil society groups condemned the brazen monetization of the electoral process and called for electoral reforms.",
            "extract": "Ondo Decides: Cash-for-Votes Scandal Exposed\n\nThe Ondo State gubernatorial election exposed the depths of vote buying in Nigerian politics as party agents openly distributed cash to voters across the state. In Akure, Owo, and Ondo town, voters were seen collecting money ranging from N2,000 to N5,000 before casting their ballots. Videos of the cash distribution went viral on social media, showing party agents counting money openly at polling units. Security agencies made minimal arrests despite the brazen violations. Opposition parties accused INEC of failing to enforce electoral laws. Anti-corruption groups called for prosecution of those involved in vote buying.",
            "filename": "2020/October 2020/Punch October 10_2020_Pg 1.tif",
            "keywords": "Ondo State, gubernatorial election, vote buying, cash distribution, electoral corruption, INEC failure",
            "image_path": "2020/October 2020/Punch October 10_2020_Pg 1.jpeg",
            "topics": "Industrial-scale vote buying, Cash-for-votes, Viral videos, Minimal enforcement, Electoral reform calls",
            "publication": "Punch",
            "publication_date": "2020/10/10",
            "page": "1",
            "tags": "ondo, corruption"
        },
        # 2021
        {
            "id": "fake_2021_001",
            "summary": "Anambra State gubernatorial election faced threats from IPOB and other separatist groups calling for election boycott. Despite heavy security, voter turnout was extremely low. Several communities recorded zero votes amid fears of violence.",
            "extract": "Anambra Guber: Low Turnout as IPOB Enforces Sit-At-Home\n\nThe Anambra State gubernatorial election recorded abysmally low voter turnout as IPOB's sit-at-home order kept residents indoors across the state. In Onitsha, Nnewi, and Awka, streets were deserted as voters stayed home fearing separatist violence. Several polling units recorded zero votes throughout the day. Security forces patrolled empty streets while INEC officials waited at deserted polling centers. Only a few brave voters came out in areas with heavy military presence. The low turnout raised questions about the legitimacy of whoever emerged winner. Political parties blamed INEC for poor timing and inadequate voter mobilization.",
            "filename": "2021/November 2021/ThisDay November 06_2021_Pg 1.tif",
            "keywords": "Anambra State, gubernatorial election, IPOB, sit-at-home, low voter turnout, separatist threats",
            "image_path": "2021/November 2021/ThisDay November 06_2021_Pg 1.jpeg",
            "topics": "Sit-at-home order, Extremely low turnout, Separatist intimidation, Zero votes recorded, Legitimacy questions",
            "publication": "ThisDay",
            "publication_date": "2021/11/06",
            "page": "1",
            "tags": "anambra, ipob"
        },
        {
            "id": "fake_2021_002",
            "summary": "FCT Area Council elections were disrupted by thugs who attacked INEC officials and voters. Several polling units were set ablaze, and ballot boxes were snatched. The police made multiple arrests, but violence continued in several areas.",
            "extract": "FCT Elections: Thugs Run Riot, Polling Units Torched\n\nArea Council elections in the Federal Capital Territory turned violent as political thugs attacked polling units, INEC officials, and voters across Abuja. In Gwagwalada, Kwali, and Bwari, armed groups stormed polling centers, setting fire to election materials and snatching ballot boxes. At least 5 people were injured in the violence. The police arrested 28 suspected thugs, recovering weapons including guns and machetes. Opposition parties accused the ruling party of sponsoring the violence to manipulate results. INEC cancelled elections in 15 polling units due to over-voting and violence.",
            "filename": "2021/February 2021/Daily Trust February 13_2021_Pg 2.tif",
            "keywords": "FCT, Area Council elections, political thugs, arson, ballot snatching, INEC attacks",
            "image_path": "2021/February 2021/Daily Trust February 13_2021_Pg 2.jpeg",
            "topics": "Thug attacks, Polling units burned, Ballot box snatching, Weapon seizures, Election cancellation",
            "publication": "Daily Trust",
            "publication_date": "2021/02/13",
            "page": "2",
            "tags": "fct, violence"
        },
        # 2022
        {
            "id": "fake_2022_001",
            "summary": "Ekiti State gubernatorial election saw improved security but vote buying remained rampant. Party agents openly distributed cash despite police presence. Civil society groups documented systematic vote buying across the state.",
            "extract": "Ekiti Guber: Vote Buying Persists Despite Security\n\nThe Ekiti State gubernatorial election witnessed brazen vote buying despite heavy security deployment meant to curb the practice. In all 16 local government areas, party agents distributed cash to voters, with the going rate ranging from N5,000 to N15,000 per vote. Civil society observers documented vote buying at over 70% of polling units visited. The police made only token arrests, releasing most suspects within hours. Opposition parties accused INEC and security agencies of allowing the monetization to continue unchecked.",
            "filename": "2022/June 2022/The Guardian June 18_2022_Pg 1.tif",
            "keywords": "Ekiti State, gubernatorial election, vote buying, cash for votes, electoral corruption, security failure",
            "image_path": "2022/June 2022/The Guardian June 18_2022_Pg 1.jpeg",
            "topics": "Brazen vote buying, Cash distribution, Token arrests, Systemic corruption, Reform frustration",
            "publication": "The Guardian",
            "publication_date": "2022/06/18",
            "page": "1",
            "tags": "ekiti, vote buying"
        },
        {
            "id": "fake_2022_002",
            "summary": "Osun State gubernatorial election was disrupted by thugs who snatched ballot boxes in multiple locations. INEC officials were assaulted, and several voters were injured. The election was declared inconclusive in affected areas, leading to a supplementary poll.",
            "extract": "Osun Guber: Thugs Snatch Ballot Boxes, Assault Officials\n\nThe Osun State gubernatorial election was marred by violent attacks on INEC officials and ballot box snatching across several local governments. In Ife Central, Iwo, and Ede, armed thugs stormed polling units, assaulting electoral officers and making away with ballot boxes. At least 12 INEC officials sustained injuries in the attacks. Security personnel were overwhelmed as the coordinated attacks occurred simultaneously in multiple locations. The violence forced INEC to cancel results from 20 polling units and declare the election inconclusive in affected areas.",
            "filename": "2022/July 2022/The Nation July 16_2022_Pg 1.tif",
            "keywords": "Osun State, gubernatorial election, ballot snatching, INEC assault, supplementary election, coordinated attacks",
            "image_path": "2022/July 2022/The Nation July 16_2022_Pg 1.jpeg",
            "topics": "Ballot box theft, INEC officials assaulted, Coordinated violence, Election declared inconclusive, Supplementary poll",
            "publication": "The Nation",
            "publication_date": "2022/07/16",
            "page": "1",
            "tags": "osun, violence"
        },
        # 2023
        {
            "id": "fake_2023_001",
            "summary": "The 2023 presidential election faced massive logistical challenges as INEC's new BVAS technology failed in many polling units. Violence erupted in Lagos, Rivers, and Kano states. Opposition parties alleged widespread rigging and called for cancellation of results.",
            "extract": "Presidential Poll: BVAS Failure, Violence Mar Exercise\n\nNigeria's 2023 presidential election was plagued by widespread BVAS technology failures that left millions of voters unable to cast their ballots. Across Lagos, Kano, Rivers, and Abuja, the biometric accreditation system malfunctioned, causing hours of delays. In Lagos, political thugs attacked polling units in Oshodi, Surulere, and Eti-Osa, destroying election materials and assaulting voters perceived to support opposition parties. At least 18 people were killed in election-related violence across the country. Opposition presidential candidates Peter Obi and Atiku Abubakar rejected the results, alleging collusion between INEC and the ruling party.",
            "filename": "2023/February 2023/Punch February 25_2023_Pg 1.tif",
            "keywords": "presidential election, BVAS failure, electoral violence, Lagos attacks, ballot snatching, opposition rejection",
            "image_path": "2023/February 2023/Punch February 25_2023_Pg 1.jpeg",
            "topics": "Technology failure, Mass disenfranchisement, Targeted political violence, Ballot theft, Results disputed",
            "publication": "Punch",
            "publication_date": "2023/02/25",
            "page": "1",
            "tags": "presidential, bvas"
        },
        {
            "id": "fake_2023_002",
            "summary": "Gubernatorial elections in Rivers, Kano, and Adamawa states were marred by violence and allegations of result manipulation. In Rivers, the Resident Electoral Commissioner was accused of partisanship. Adamawa's election was suspended mid-collation in controversial circumstances.",
            "extract": "Guber Elections: Rivers, Adamawa Polls in Crisis\n\nGovernatorial elections in several states descended into crisis as violence and accusations of result manipulation dominated the exercise. In Rivers State, opposition parties accused the Resident Electoral Commissioner of open partisanship, alleging he manipulated results in favor of the ruling party. Violent clashes between APC and PDP supporters left at least 14 people dead across the state. In Adamawa, INEC suspended the collation of results in controversial circumstances after the Resident Electoral Commissioner allegedly tried to announce results without completing the process. The electoral crisis deepened distrust in INEC's ability to conduct credible elections.",
            "filename": "2023/March 2023/Vanguard March 18_2023_Pg 1.tif",
            "keywords": "gubernatorial elections, Rivers State, Adamawa, REC partisanship, result manipulation, election suspension",
            "image_path": "2023/March 2023/Vanguard March 18_2023_Pg 1.jpeg",
            "topics": "REC partisanship allegations, Collation suspended, Inter-party violence, Result manipulation, INEC credibility crisis",
            "publication": "Vanguard",
            "publication_date": "2023/03/18",
            "page": "1",
            "tags": "gubernatorial, crisis"
        },
    ]

    results = []
    for data in fake_data:
        doc = _FakeDocument(id=data["id"], struct_data=data)
        results.append(_FakeResult(document=doc))

    return results