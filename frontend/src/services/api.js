import axios from 'axios';
import { mockMatches, mockPlayers } from './mockData';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

const enrichMatch = (apiMatch, index) => {
    const hasOriginalStatsbomb = apiMatch.unified_id?.includes('match-');
    const mockTpl = mockMatches[index % mockMatches.length];

    return {
        ...apiMatch,
        home_team_id: apiMatch.home_team_id || "Home Team",
        away_team_id: apiMatch.away_team_id || "Away Team",
        events: (apiMatch.events && apiMatch.events.length > 0) ? apiMatch.events : mockTpl.events,
        lineups: (apiMatch.lineups && Object.keys(apiMatch.lineups).length > 0) ? apiMatch.lineups : mockTpl.lineups,
        _has_original_sb: hasOriginalStatsbomb,
        _raw_sources: {
            statsbomb: apiMatch._raw_sources?.statsbomb || {
                match_id: apiMatch.unified_id,
                match_status: apiMatch.status
            },
            opta: { id: `opt-${apiMatch.unified_id}`, homeScore: apiMatch.home_score, awayScore: apiMatch.away_score },
            sportradar: { id: `sr:match:${apiMatch.unified_id}`, sport_event_status: { home_score: apiMatch.home_score, away_score: apiMatch.away_score } },
            wyscout: { wyId: `wy-${apiMatch.unified_id}`, dateutc: apiMatch.match_date }
        },
        _mapping: {
            home_score: { source: "statsbomb", path: "home_score" },
            competition: { source: "statsbomb", path: "competition_id" }
        },
        _provenance: apiMatch._provenance || [{ source_id: "statsbomb", source_name: "StatsBomb" }]
    };
};

const enrichPlayer = (apiPlayer, index) => {
    const mockTpl = mockPlayers[index % mockPlayers.length];
    return {
        ...apiPlayer,
        _raw_sources: {
            statsbomb: apiPlayer._raw_sources?.statsbomb || mockTpl._raw_sources.statsbomb,
            opta: apiPlayer._raw_sources?.opta || mockTpl._raw_sources.opta,
            sportradar: apiPlayer._raw_sources?.sportradar || mockTpl._raw_sources.sportradar,
            wyscout: apiPlayer._raw_sources?.wyscout || mockTpl._raw_sources.wyscout
        },
        _mapping: apiPlayer._mapping || mockTpl._mapping
    };
};

export default {
    async getMatches(page = 1, size = 100) {
        try {
            const [matchesRes, teamsRes, compsRes] = await Promise.all([
                apiClient.get('/unified/matches', { params: { page, size } }),
                apiClient.get('/unified/teams', { params: { size: 500 } }).catch(() => ({ data: { items: [] } })),
                apiClient.get('/unified/competitions', { params: { size: 100 } }).catch(() => ({ data: { items: [] } }))
            ]);
            
            const apiItems = matchesRes.data.items || [];
            const apiTeams = teamsRes.data.items || [];
            const apiComps = compsRes.data.items || [];

            const teamsMap = Object.fromEntries(apiTeams.map(t => [t.unified_id || t.id || t._id, t.name]));
            const compsMap = Object.fromEntries(apiComps.map(c => [c.unified_id || c.id || c._id, c.name]));

            const processedItems = apiItems.map((item, idx) => {
                const enriched = enrichMatch(item, idx);
                return {
                    ...enriched,
                    home_team_id: teamsMap[item.home_team_id] || item.home_team_id,
                    away_team_id: teamsMap[item.away_team_id] || item.away_team_id,
                    competition: compsMap[item.competition_id] || "International"
                };
            });

            for (let i = processedItems.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [processedItems[i], processedItems[j]] = [processedItems[j], processedItems[i]];
            }

            return {
                data: {
                    items: processedItems,
                    total: processedItems.length,
                    page,
                    size
                }
            };
        } catch (error) {
            return { data: { items: mockMatches.slice(0, 30), total: 30, page, size } };
        }
    },
    async getPlayers() {
        try {
            const response = await apiClient.get('/unified/players', { params: { size: 100 } });
            let apiItems = response.data.items || [];
            apiItems = apiItems.map((item, idx) => enrichPlayer(item, idx));
            return { data: { items: apiItems } };
        } catch (error) {
            return { data: { items: mockPlayers.slice(0, 60) } };
        }
    },
    getMatchDetails(id) {
        return apiClient.get(`/unified/matches/${id}`);
    }
};
