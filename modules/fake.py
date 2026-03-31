from modules.shape import Source, Date, Entry, EnrichedCluster

# enrich.py

def fake_enriched_clusters():
    """Return 10 mock EnrichedCluster results for frontend/testing purposes."""
 
    def _src(filename, pub, publication, page, extract):
        return Source(
            summary=extract,
            extract=extract,
            filename=filename,
            keywords=["nigeria", "history"],
            image_path=f"/images/{filename.replace('.pdf', '.jpg')}",
            topics=["politics"],
            publication=publication,
            publication_date=Date(*pub),  # (day, month, year)
            page=page,
            tags=["mock"],
            relevant_extract=extract,
        )
 
    def _e(id, src, relevance):
        return Entry(id=id, source=src, semantic_relevance=relevance)
 
    mock_data = [
        {
            "label": "Oct 1960",
            "title": "Nigeria Gains Independence from Britain",
            "summary": "On October 1, 1960, Nigeria officially became an independent nation. Prime Minister Tafawa Balewa addressed the nation as the Union Jack was lowered and the green-white-green flag was raised at Tafawa Balewa Square in Lagos, watched by thousands of jubilant citizens and foreign dignitaries.",
            "entries": [
                _e("001", _src("daily_times_1960_10_01.pdf", (1, 10, 1960), "Daily Times", 1, "Nigeria is free! Thousands gather at Tafawa Balewa Square as the green-white-green flag is hoisted for the first time."), 0.97),
                _e("002", _src("west_african_pilot_1960_10_02.pdf", (2, 10, 1960), "West African Pilot", 1, "Celebrations continue across the Western and Eastern regions as Nigeria savours its first days as a sovereign state."), 0.91),
            ],
        },
        {
            "label": "Jan 1966",
            "title": "First Military Coup Topples the First Republic",
            "summary": "A group of army majors staged a bloody coup on January 15, 1966, killing Prime Minister Balewa, Premier Akintola, and Premier Bello. Major General Aguiyi-Ironsi assumed power as head of the Federal Military Government.",
            "entries": [
                _e("003", _src("daily_times_1966_01_16.pdf", (16, 1, 1966), "Daily Times", 1, "Military officers seize power overnight; PM Balewa reported missing. Bodies of Premier Akintola found in Ibadan."), 0.95),
                _e("004", _src("nigerian_tribune_1966_01_17.pdf", (17, 1, 1966), "Nigerian Tribune", 1, "Ironsi broadcasts to the nation, declares martial law. 'The military has no desire to rule,' he assures citizens."), 0.88),
            ],
        },
        {
            "label": "Jul 1967 – Jan 1970",
            "title": "The Biafran War Engulfs the Southeast",
            "summary": "Colonel Ojukwu declared the Republic of Biafra on May 30, 1967, plunging Nigeria into a devastating civil war that lasted 30 months. Federal forces enforced a naval blockade that led to mass starvation, killing an estimated one to three million civilians.",
            "entries": [
                _e("005", _src("new_nigerian_1967_07_08.pdf", (8, 7, 1967), "New Nigerian", 1, "Federal troops advance on Nsukka as war begins in earnest. Gowon vows to preserve Nigeria's unity at all costs."), 0.96),
                _e("006", _src("daily_sketch_1969_03_14.pdf", (14, 3, 1969), "Daily Sketch", 3, "Relief agencies warn of mass starvation in besieged Biafra. Red Cross airlifts face obstruction from both sides."), 0.85),
                _e("007", _src("new_nigerian_1970_01_13.pdf", (13, 1, 1970), "New Nigerian", 1, "Biafra surrenders unconditionally. Gowon declares 'No victor, no vanquished' and announces reconciliation policy."), 0.93),
            ],
        },
        {
            "label": "Feb 1976",
            "title": "Assassination of Murtala Mohammed Shocks Nation",
            "summary": "Head of State General Murtala Mohammed was assassinated in a failed coup attempt on February 13, 1976, shot in his staff car in Lagos traffic. His deputy, Olusegun Obasanjo, succeeded him and vowed to continue the transition to civilian rule.",
            "entries": [
                _e("008", _src("daily_times_1976_02_14.pdf", (14, 2, 1976), "Daily Times", 1, "Gen Murtala shot dead in his Mercedes on the way to Dodan Barracks. Col. Dimka leads abortive takeover attempt."), 0.94),
                _e("009", _src("nigerian_tribune_1976_02_15.pdf", (15, 2, 1976), "Nigerian Tribune", 1, "Obasanjo addresses grieving nation, pledges stability and continuation of Murtala's anti-corruption reforms."), 0.82),
            ],
        },
        {
            "label": "Oct 1979",
            "title": "Shehu Shagari Inaugurated in Return to Civilian Rule",
            "summary": "After 13 years of military governance, Nigeria returned to democratic rule with the inauguration of President Shehu Shagari on October 1, 1979. The Second Republic adopted a US-style presidential system under a new constitution.",
            "entries": [
                _e("010", _src("new_nigerian_1979_10_01.pdf", (1, 10, 1979), "New Nigerian", 1, "Shagari sworn in as the first executive president of Nigeria at a ceremony attended by dozens of world leaders."), 0.90),
                _e("011", _src("daily_times_1979_10_02.pdf", (2, 10, 1979), "Daily Times", 2, "Commentators hopeful but warn of ethnic tensions and the fragility of the nascent democratic institutions."), 0.78),
            ],
        },
        {
            "label": "Dec 1983",
            "title": "Buhari Overthrows Shagari in Bloodless Coup",
            "summary": "On December 31, 1983, Major General Muhammadu Buhari seized power in a bloodless coup, citing rampant corruption, economic mismanagement, and the collapse of oil revenues under the Shagari administration.",
            "entries": [
                _e("012", _src("daily_times_1984_01_02.pdf", (2, 1, 1984), "Daily Times", 1, "Military back in charge: Buhari announces Supreme Military Council, suspends the constitution, and detains politicians."), 0.92),
                _e("013", _src("the_guardian_1984_01_03.pdf", (3, 1, 1984), "The Guardian", 1, "War Against Indiscipline campaign launched nationwide. Citizens ordered to form orderly queues at bus stops."), 0.80),
            ],
        },
        {
            "label": "Jun 1993",
            "title": "Annulment of June 12 Election Sparks National Crisis",
            "summary": "The military government of General Babangida annulled the June 12, 1993 presidential election—widely accepted as the freest in Nigerian history—believed won by MKO Abiola. The annulment triggered mass protests, strikes, and a prolonged political crisis.",
            "entries": [
                _e("014", _src("the_guardian_1993_06_13.pdf", (13, 6, 1993), "The Guardian", 1, "Babangida annuls what observers call the freest and fairest election in Nigerian history. Results had shown Abiola leading."), 0.98),
                _e("015", _src("nigerian_tribune_1993_06_25.pdf", (25, 6, 1993), "Nigerian Tribune", 1, "Lagos erupts in protest; NADECO calls for civil disobedience. Oil workers threaten to shut down the refineries."), 0.91),
                _e("016", _src("daily_champion_1993_07_05.pdf", (5, 7, 1993), "Daily Champion", 2, "Babangida 'steps aside', installs businessman Ernest Shonekan as head of an Interim National Government."), 0.76),
            ],
        },
        {
            "label": "Nov 1995",
            "title": "Execution of Ken Saro-Wiwa Draws Global Condemnation",
            "summary": "The Abacha regime hanged writer and Ogoni activist Ken Saro-Wiwa alongside eight others on November 10, 1995, despite international pleas for clemency. The executions triggered Nigeria's suspension from the Commonwealth and widespread diplomatic sanctions.",
            "entries": [
                _e("017", _src("the_guardian_1995_11_11.pdf", (11, 11, 1995), "The Guardian", 1, "Saro-Wiwa and eight Ogoni activists hanged at Port Harcourt prison despite worldwide appeals for clemency."), 0.96),
                _e("018", _src("vanguard_1995_11_13.pdf", (13, 11, 1995), "Vanguard", 1, "Commonwealth suspends Nigeria. US, EU, and South Africa recall ambassadors. Shell faces global boycott calls."), 0.84),
            ],
        },
        {
            "label": "May 1999",
            "title": "Obasanjo Sworn In as Democracy Returns",
            "summary": "Former military ruler Olusegun Obasanjo was inaugurated as civilian president on May 29, 1999, marking the start of the Fourth Republic after 16 years of military dictatorship under Buhari, Babangida, and Abacha.",
            "entries": [
                _e("019", _src("thisday_1999_05_30.pdf", (30, 5, 1999), "ThisDay", 1, "Obasanjo takes the oath of office at Eagle Square. Promises to fight corruption, rebuild the economy, and unite a fractured Nigeria."), 0.93),
                _e("020", _src("the_guardian_1999_05_31.pdf", (31, 5, 1999), "The Guardian", 1, "International community welcomes Nigeria's return to democracy. Clinton and Blair among first to send congratulations."), 0.79),
            ],
        },
        {
            "label": "Apr 2014",
            "title": "Chibok Schoolgirls Kidnapped by Boko Haram",
            "summary": "On April 14, 2014, Boko Haram militants stormed the Government Girls Secondary School in Chibok, Borno State, abducting 276 schoolgirls. The government's slow response sparked the global #BringBackOurGirls campaign and intense criticism of President Jonathan's handling of the insurgency.",
            "entries": [
                _e("021", _src("vanguard_2014_04_16.pdf", (16, 4, 2014), "Vanguard", 1, "276 girls taken from Chibok boarding school at night. Military was warned of imminent attack but failed to reinforce."), 0.99),
                _e("022", _src("premium_times_2014_04_25.pdf", (25, 4, 2014), "Premium Times", 1, "#BringBackOurGirls trends worldwide. Protests mount in Abuja and Lagos demanding government action."), 0.94),
                _e("023", _src("thisday_2014_05_05.pdf", (5, 5, 2014), "ThisDay", 2, "Michelle Obama, Malala Yousafzai join global chorus demanding rescue. Jonathan government faces mounting international pressure."), 0.81),
            ],
        },
    ]
 
    enriched_clusters = {}
    for i, data in enumerate(mock_data):
        entries = data["entries"]
        enriched = EnrichedCluster(
            index       = i,
            label       = data["label"],
            title       = data["title"],
            summary     = data["summary"],
            entries     = entries,
            start_date  = entries[0].source.publication_date,
            end_date    = entries[-1].source.publication_date,
            cover_story = max(entries, key=lambda e: e.semantic_relevance),
        )
        enriched_clusters[data["label"]] = enriched
 
    return enriched_clusters



# fetch.py


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


def fake_search_results() -> list:
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
