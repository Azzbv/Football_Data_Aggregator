// 1. Team Registry
export const mockTeams = {
  "T1": { id: "T1", name: "Lions FC", city: "Lyon", stadium: "Lion Arena", colors: ["#FFD700", "#B22222"] },
  "T2": { id: "T2", name: "Eagles Utd", city: "London", stadium: "Eagle Nest", colors: ["#FFFFFF", "#000080"] },
  "T3": { id: "T3", name: "Bears City", city: "Berlin", stadium: "Bear Den", colors: ["#000000", "#FFD700"] },
  "T4": { id: "T4", name: "Wolves SC", city: "Rome", stadium: "Wolf Stadium", colors: ["#8B0000", "#FFD700"] },
  "T5": { id: "T5", name: "Sharks FC", city: "Miami", stadium: "Shark Tank", colors: ["#00CED1", "#FFFFFF"] },
  "T6": { id: "T6", name: "Whales SC", city: "Sydney", stadium: "Ocean Reef", colors: ["#4682B4", "#FFFFFF"] },
  "T7": { id: "T7", name: "Tigers FC", city: "Tokyo", stadium: "Tiger Dome", colors: ["#FFA500", "#000000"] },
  "T8": { id: "T8", name: "Panthers SC", city: "Munich", stadium: "Panther Park", colors: ["#000000", "#FFFFFF"] },
  "T9": { id: "T9", name: "Cobra FC", city: "Cairo", stadium: "Desert Stadium", colors: ["#FFFF00", "#000000"] },
  "T10": { id: "T10", name: "Dragons Utd", city: "Wales", stadium: "Dragon Valley", colors: ["#FF0000", "#008000"] },
  "T11": { id: "T11", name: "Real Madrid", city: "Madrid", stadium: "Bernabéu" },
  "T12": { id: "T12", name: "FC Barcelona", city: "Barcelona", stadium: "Camp Nou" },
  "T13": { id: "T13", name: "Atlético Madrid", city: "Madrid", stadium: "Metropolitano" },
  "T14": { id: "T14", name: "Sevilla FC", city: "Sevilla", stadium: "Pizjuán" },
  "T15": { id: "T15", name: "Manchester City", city: "Manchester", stadium: "Etihad" },
  "T16": { id: "T16", name: "Argentina", city: "Buenos Aires", stadium: "Monumental" },
  "T17": { id: "T17", name: "France", city: "Paris", stadium: "Stade de France" },
  "T18": { id: "T18", name: "Bayern Munich", city: "Munich", stadium: "Allianz Arena" },
  "T19": { id: "T19", name: "Paris SG", city: "Paris", stadium: "Parc des Princes" },
  "T20": { id: "T20", name: "Arsenal Women", city: "London", stadium: "Emirates" },
  "T21": { id: "T21", name: "Chelsea Women", city: "London", stadium: "Kingsmeadow" }
};

// 2. League-Team buckets
const teamsByLeague = {
  "La Liga": ["T11", "T12", "T13", "T14"],
  "Premier League": ["T2", "T3", "T9", "T15"],
  "FIFA World Cup": ["T16", "T17", "T7", "T10"],
  "Champions League": ["T1", "T8", "T18", "T19"],
  "FA Women's Super League": ["T5", "T6", "T20", "T21"]
};

// 3. Player Generation
const generateRealPlayers = () => {
  const realBase = [
    { id: "p_1", name: "Lionel Messi", nationality: "Argentina", birth_date: "1987-06-24", position: "Right Wing" },
    { id: "p_2", name: "Cristiano Ronaldo", nationality: "Portugal", birth_date: "1985-02-05", position: "Forward" },
    { id: "p_3", name: "Kevin De Bruyne", nationality: "Belgium", birth_date: "1991-06-28", position: "Midfielder" },
    { id: "p_4", name: "Kylian Mbappé", nationality: "France", birth_date: "1998-12-20", position: "Forward" },
    { id: "p_5", name: "Erling Haaland", nationality: "Norway", birth_date: "2000-07-21", position: "Forward" },
    { id: "p_6", name: "Mohamed Salah", nationality: "Egypt", birth_date: "1992-06-15", position: "Forward" },
    { id: "p_7", name: "Virgil van Dijk", nationality: "Netherlands", birth_date: "1991-07-08", position: "Defender" },
    { id: "p_8", name: "Robert Lewandowski", nationality: "Poland", birth_date: "1988-08-21", position: "Forward" },
    { id: "p_9", name: "Luka Modric", nationality: "Croatia", birth_date: "1985-09-09", position: "Midfielder" },
    { id: "p_10", name: "Harry Kane", nationality: "England", birth_date: "1993-07-28", position: "Forward" },
    { id: "p_11", name: "Alisson Becker", nationality: "Brazil", birth_date: "1992-10-02", position: "Goalkeeper" },
    { id: "p_12", name: "Ruben Dias", nationality: "Portugal", birth_date: "1997-05-14", position: "Defender" },
  ];

  const players = [...realBase];
  const firstNames = ["James", "Thomas", "Antoine", "Sergio", "Luka", "Marcus", "Bernardo", "Phil", "Bukayo", "Gabriel", "Rodri", "Enzo", "Julian", "Bruno", "Heung-min", "Son"];
  const lastNames = ["Silva", "Griezmann", "Ramos", "Foden", "Saka", "Martinelli", "Hernandez", "Fernandez", "Alvarez", "Gundogan", "Pedri", "Gavi", "Bellingham", "Rice"];

  for (let i = 13; i <= 200; i++) {
    const fn = firstNames[i % firstNames.length];
    const ln = lastNames[i % lastNames.length];
    players.push({
      id: `p_${i}`,
      name: `${fn} ${ln}`,
      nationality: "Global",
      birth_date: `19${90 + (i % 12)}-05-10`,
      position: i % 3 === 0 ? "Forward" : (i % 2 === 0 ? "Midfielder" : "Defender")
    });
  }

  return players.map(p => ({
    ...p,
    _raw_sources: {
      statsbomb: { player_id: Math.floor(Math.random() * 10000), player_name: p.name, country: { name: p.nationality } },
      opta: { id: `opt_${p.id}`, firstName: p.name.split(' ')[0], lastName: p.name.split(' ')[1] },
      sportradar: { id: `sr:player:${Math.floor(Math.random() * 99999)}`, full_name: p.name, date_of_birth: p.birth_date, type: "player" },
      wyscout: { wyId: Math.floor(Math.random() * 50000), shortName: p.name.split(' ').pop(), role: { name: p.position } }
    },
    _mapping: {
      name: { source: "statsbomb", path: "player_name", explanation: "Verified name from StatsBomb's player registry." },
      nationality: { source: "statsbomb", path: "country.name", explanation: "Normalized full country string." },
      birth_date: { source: "sportradar", path: "date_of_birth", explanation: "Sportradar acts as administrative ground truth for player biometrics." },
      position: { source: "wyscout", path: "role.name", explanation: "Wyscout's tactical roles align best with our video scouting downstream consumers." }
    }
  }));
};

export const mockPlayers = generateRealPlayers();

// 4. Lineup Generation
const generateLineup = (teamId, startIndex) => {
  const teamPlayers = [];
  for (let i = 0; i < 11; i++) {
    const playerIndex = (startIndex + i) % mockPlayers.length;
    teamPlayers.push({
      player_id: mockPlayers[playerIndex].id,
      player_name: mockPlayers[playerIndex].name,
      jersey_number: i + 1,
      position: mockPlayers[playerIndex].position,
      is_starting: true
    });
  }
  return teamPlayers;
};

// 5. Event Generation
const generateEvents = (matchId) => {
  const types = ["Pass", "Shot", "Ball Recovery", "Foul Committed", "Duel", "Interception", "Clearance", "Tackle"];
  return Array.from({ length: 150 }, (_, i) => {
    const minute = Math.floor(i * 0.63);
    const second = (i * 17) % 60;
    const type = types[i % types.length];
    
    let outcome = "Complete";
    if (type === "Shot") {
      outcome = (i % 5 === 0 || i % 7 === 0) ? "Goal" : "Saved";
    } else {
      outcome = i % 3 === 0 ? "Incomplete" : "Complete";
    }
    
    return {
      id: `${matchId}_ev_${i + 1}`,
      type: type,
      minute: minute,
      second: second,
      player_id: mockPlayers[i % 22]?.id || mockPlayers[0].id,
      team_id: i % 2 === 0 ? "T1" : "T2",
      outcome: outcome,
      _raw_sources: {
        statsbomb: { 
          id: `sb_${matchId}_${i}`, 
          type: { id: i % 50, name: type }, 
          minute: minute,
          location: [Math.random() * 120, Math.random() * 80],
          play_pattern: { id: 1, name: "Regular Play" }
        },
        opta: { 
          id: `opt_${matchId}_${i}`, 
          typeId: i % 10, 
          min: minute,
          sec: second,
          qualifiers: [{ id: 56, value: "Zone" }, { id: 213, value: "Angle" }]
        },
        sportradar: {
          id: `sr:match_event:${matchId}_${i}`,
          type: type.toLowerCase().replace(' ', '_'),
          time: `${minute}:${second}`
        },
        wyscout: {
          id: `wy_${matchId}_${i}`,
          eventName: type,
          subEventName: outcome,
          matchPeriod: minute > 45 ? "2H" : "1H",
          eventSec: (minute * 60) + second
        }
      },
      _mapping: {
        type: { source: "statsbomb", path: "type.name", explanation: "Direct mapping from StatsBomb's highly granular event ontology." },
        minute: { source: "opta", path: "min", explanation: "Preferred timing from Opta's low-latency real-time feed." },
        outcome: { source: "wyscout", path: "subEventName", explanation: "Wyscout's subEvent tagging is deeply verified by video review." }
      }
    };
  });
};

// 6. Match Generation
const generateMatches = (count) => {
  const leagues = [
    { name: "La Liga", country: "Spain" },
    { name: "Premier League", country: "England" },
    { name: "FIFA World Cup", country: "International" },
    { name: "Champions League", country: "Europe" },
    { name: "FA Women's Super League", country: "England" }
  ];

  const baseDate = new Date("2026-08-01T15:00:00Z");

  return Array.from({ length: count }, (_, i) => {
    const matchId = `match_${i + 1}`;
    const league = leagues[i % leagues.length];
    const leagueTeams = teamsByLeague[league.name];
    
    const homeId = leagueTeams[i % leagueTeams.length];
    const awayId = leagueTeams[(i + 1) % leagueTeams.length];
    
    const matchDate = new Date(baseDate);
    matchDate.setDate(matchDate.getDate() + i);

    return {
      id: matchId,
      competition: league.name,
      match_date: matchDate.toISOString(),
      home_team: mockTeams[homeId],
      away_team: mockTeams[awayId],
      home_score: (i % 3) + (i % 2),
      away_score: i % 2,
      status: i % 5 === 0 ? "live" : "played",
      lineups: { 
        home: generateLineup(homeId, i * 2), 
        away: generateLineup(awayId, (i * 2) + 11) 
      },
      events: generateEvents(matchId),
      _provenance: [
        { source_id: "statsbomb", source_name: "StatsBomb", record_id: `sb-m-${i}` }
      ],
      _raw_sources: {
        statsbomb: { 
          match_id: 1000 + i, 
          competition: { country_name: league.country, competition_name: league.name },
          home_team: { home_team_name: mockTeams[homeId].name },
          away_team: { away_team_name: mockTeams[awayId].name }
        }
      }
    };
  });
};

export const mockMatches = generateMatches(250);
