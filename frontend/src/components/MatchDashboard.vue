<template>
  <v-container fluid>
    <v-tabs v-model="mainTab" color="primary" align-tabs="start" class="mb-6 border-bottom">
      <v-tab value="overview"><v-icon start>mdi-view-dashboard</v-icon> Live Overview</v-tab>
      <v-tab value="explorer"><v-icon start>mdi-database-search</v-icon> Unified Explorer</v-tab>
    </v-tabs>

    <v-window v-model="mainTab">
      <v-window-item value="overview">
        <v-row>
          <v-col cols="12">
            <v-card elevation="2">
              <v-card-title class="d-flex align-center py-4">
                <v-icon icon="mdi-soccer" start color="primary"></v-icon>
                Unified Match Statistics
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  variant="elevated"
                  prepend-icon="mdi-refresh"
                  @click="fetchMatches"
                  :loading="loading"
                >
                  Refresh
                </v-btn>
              </v-card-title>
              <v-divider></v-divider>
              <v-data-table
                :headers="headers"
                :items="matches"
                :loading="loading"
                class="elevation-0"
                hover
              >
                <template v-slot:item.match_date="{ item }">
                  {{ formatDate(item.match_date) }}
                </template>
                <template v-slot:item.home_team_id="{ item }">
                  <span class="font-weight-bold text-blue-darken-2">{{ item.home_team_id }}</span>
                </template>
                <template v-slot:item.away_team_id="{ item }">
                  <span class="font-weight-bold text-red-darken-2">{{ item.away_team_id }}</span>
                </template>
                <template v-slot:item.score="{ item }">
                  <v-chip color="blue-grey-darken-3" variant="outlined" size="small">
                    {{ item.home_score }} - {{ item.away_score }}
                  </v-chip>
                </template>
                <template v-slot:item.status="{ item }">
                  <v-chip
                    :color="item.status === 'played' ? 'success' : 'warning'"
                    size="x-small"
                    variant="tonal"
                    class="text-uppercase"
                  >
                    {{ item.status }}
                  </v-chip>
                </template>
                <template v-slot:item.provenance="{ item }">
                  <div v-if="item._provenance" class="d-flex flex-wrap gap-1">
                    <v-chip
                      v-for="link in item._provenance"
                      :key="link.source_id"
                      size="x-small"
                      variant="outlined"
                      class="ma-1"
                    >
                      {{ link.source_name }}
                    </v-chip>
                  </div>
                </template>
                <template v-slot:item.actions="{ item }">
                  <v-btn
                    icon="mdi-swap-horizontal"
                    variant="text"
                    color="info"
                    size="small"
                    @click="showTransformation(item)"
                    title="View Transformation"
                  ></v-btn>
                </template>
              </v-data-table>
            </v-card>
          </v-col>
        </v-row>

        <v-row class="mt-8">
          <v-col cols="12">
            <v-card elevation="2">
              <v-card-title class="d-flex align-center py-4 bg-blue-grey-lighten-5">
                <v-icon icon="mdi-account-group" start color="secondary"></v-icon>
                Unified Player Registry
                <v-spacer></v-spacer>
                <v-text-field
                  v-model="playerSearch"
                  prepend-inner-icon="mdi-magnify"
                  label="Search Players"
                  single-line
                  hide-details
                  density="compact"
                  variant="outlined"
                  max-width="300"
                ></v-text-field>
              </v-card-title>
              <v-data-table
                :headers="playerHeaders"
                :items="players"
                :search="playerSearch"
                class="elevation-0"
                hover
              >
                <template v-slot:item.actions="{ item }">
                  <v-btn
                    icon="mdi-swap-horizontal"
                    variant="text"
                    color="secondary"
                    size="small"
                    @click="showTransformation(item)"
                    title="View Transformation"
                  ></v-btn>
                </template>
              </v-data-table>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item value="explorer">
        <v-row>
          <v-col cols="12" md="4">
            <v-card elevation="2" class="explorer-sidebar">
              <v-card-title class="bg-blue-grey-lighten-4 sticky-header">
                <v-icon icon="mdi-filter" start></v-icon> Entity Explorer
              </v-card-title>
              
              <v-list density="compact" nav class="explorer-list">
                <v-list-subheader class="sticky-header bg-white">UNIFIED MATCHES ({{ matches.length }})</v-list-subheader>
                <v-list-item
                  v-for="match in matches"
                  :key="match.id"
                  :active="explorerMatch?.id === match.id"
                  @click="explorerMatch = match; explorerType = 'match'; explorerSubTab = 'lineups'"
                  prepend-icon="mdi-soccer"
                >
                  <v-list-item-title class="font-weight-bold">{{ match.home_team?.name || match.home_team_id }} v {{ match.away_team?.name || match.away_team_id }}</v-list-item-title>
                  <v-list-item-subtitle>{{ formatDate(match.match_date) }}</v-list-item-subtitle>
                </v-list-item>

                <v-divider class="my-2"></v-divider>
                <v-list-subheader class="sticky-header bg-white">UNIFIED PLAYERS ({{ players.length }})</v-list-subheader>
                <v-list-item
                  v-for="player in players"
                  :key="player.id"
                  :active="explorerPlayer?.id === player.id"
                  @click="explorerPlayer = player; explorerType = 'player'"
                  prepend-icon="mdi-account"
                >
                  <v-list-item-title>{{ player.name }}</v-list-item-title>
                  <v-list-item-subtitle>{{ player.nationality }} • {{ player.position }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>

          <v-col cols="12" md="8">
            <div v-if="explorerType === 'match' && explorerMatch">
              <v-card elevation="2" class="mb-4 overflow-hidden">
                <v-card-text class="pa-0">
                  <v-row no-gutters class="bg-primary text-white pa-6 align-center text-center">
                    <v-col cols="12" class="mb-4">
                      <div class="text-caption text-white-50 font-weight-bold text-uppercase tracking-wide">
                        {{ explorerMatch.competition || 'International' }} • {{ formatDate(explorerMatch.match_date) }}
                      </div>
                    </v-col>
                    <v-col cols="4">
                      <div class="text-h4 font-weight-bold">{{ explorerMatch.home_team?.name }}</div>
                      <div class="text-caption">HOME</div>
                    </v-col>
                    <v-col cols="4">
                      <div class="text-h2 font-weight-black">{{ explorerMatch.home_score }} - {{ explorerMatch.away_score }}</div>
                      <v-chip color="white" variant="outlined" size="small" class="mt-2">{{ explorerMatch.status.toUpperCase() }}</v-chip>
                    </v-col>
                    <v-col cols="4">
                      <div class="text-h4 font-weight-bold">{{ explorerMatch.away_team?.name }}</div>
                      <div class="text-caption">AWAY</div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>

              <v-card elevation="2">
                <v-tabs v-model="explorerSubTab" color="primary">
                  <v-tab value="lineups"><v-icon start>mdi-account-group</v-icon> Lineups</v-tab>
                  <v-tab value="events"><v-icon start>mdi-clock-outline</v-icon> Timeline</v-tab>
                  <v-tab value="data"><v-icon start>mdi-code-json</v-icon> Raw Unified</v-tab>
                </v-tabs>

                <v-window v-model="explorerSubTab" class="pa-4">
                  <v-window-item value="lineups">
                    <v-row>
                      <v-col cols="12" md="6">
                        <div class="text-subtitle-1 font-weight-bold mb-3 border-bottom">{{ explorerMatch.home_team?.name }} Starting XI</div>
                        <v-list density="compact">
                          <v-list-item
                            v-for="p in explorerMatch.lineups?.home || []"
                            :key="p.player_id"
                            :title="p.player_name"
                            :subtitle="p.position"
                          >
                            <template v-slot:prepend>
                              <v-avatar color="grey-lighten-3" size="32" class="mr-2">
                                <span class="text-caption font-weight-bold">{{ p.jersey_number }}</span>
                              </v-avatar>
                            </template>
                          </v-list-item>
                          <v-list-item v-if="!explorerMatch.lineups?.home?.length">
                            <v-list-item-subtitle>Lineup not available</v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-col>
                      <v-col cols="12" md="6">
                        <div class="text-subtitle-1 font-weight-bold mb-3 border-bottom">{{ explorerMatch.away_team?.name || 'Away Team' }} Starting XI</div>
                        <v-list density="compact">
                          <v-list-item
                            v-for="p in explorerMatch.lineups?.away || []"
                            :key="p.player_id"
                            :title="p.player_name"
                            :subtitle="p.position"
                          >
                            <template v-slot:prepend>
                              <v-avatar color="grey-lighten-3" size="32" class="mr-2">
                                <span class="text-caption font-weight-bold">{{ p.jersey_number }}</span>
                              </v-avatar>
                            </template>
                          </v-list-item>
                          <v-list-item v-if="!explorerMatch.lineups?.away?.length">
                            <v-list-item-subtitle>Lineup not available</v-list-item-subtitle>
                          </v-list-item>
                        </v-list>
                      </v-col>
                    </v-row>
                  </v-window-item>

                  <v-window-item value="events">
                    <div class="d-flex align-center mb-4 flex-wrap gap-2">
                      <div class="text-h6 mr-4">Match Timeline</div>
                      
                      <v-chip-group v-model="eventTypeFilter" selected-class="bg-primary text-white" mandatory column>
                        <v-chip value="All" size="small" variant="outlined">All</v-chip>
                        <v-chip value="Goal" size="small" variant="outlined" color="warning">Goals</v-chip>
                        <v-chip value="Shot" size="small" variant="outlined" color="error">Shots</v-chip>
                        <v-chip value="Pass" size="small" variant="outlined" color="success">Passes</v-chip>
                        <v-chip value="Foul Committed" size="small" variant="outlined" color="deep-orange">Fouls</v-chip>
                      </v-chip-group>

                      <v-spacer></v-spacer>
                      <v-text-field
                        v-model="eventSearch"
                        label="Search events..."
                        density="compact"
                        variant="outlined"
                        hide-details
                        prepend-inner-icon="mdi-magnify"
                        max-width="200"
                      ></v-text-field>
                    </div>

                    <v-data-table
                      :headers="eventHeaders"
                      :items="filteredEvents"
                      :search="eventSearch"
                      density="compact"
                      hover
                      :items-per-page="15"
                    >
                      <template v-slot:item.minute="{ item }">
                        <span class="font-weight-bold">{{ item.minute }}'</span>
                      </template>
                      <template v-slot:item.type="{ item }">
                        <v-chip
                          size="x-small"
                          :color="getEventColor(item.type)"
                          variant="tonal"
                          class="text-uppercase"
                        >
                          {{ item.type }}
                        </v-chip>
                      </template>
                    </v-data-table>
                  </v-window-item>

                  <v-window-item value="data">
                    <div class="code-container unified-code">
                      <pre>{{ JSON.stringify(getCleanUnified(explorerMatch), null, 2) }}</pre>
                    </div>
                  </v-window-item>
                </v-window>
              </v-card>
            </div>

            <v-card v-else-if="explorerType === 'player' && explorerPlayer" elevation="2">
              <v-card-title class="bg-secondary text-white">Unified Player Profile: {{ explorerPlayer.id }}</v-card-title>
              <v-card-text class="pa-4">
                <v-row>
                  <v-col cols="12" md="4">
                    <v-avatar color="grey-lighten-2" size="150" class="mb-4 d-block mx-auto">
                      <v-icon icon="mdi-account" size="100" color="grey"></v-icon>
                    </v-avatar>
                    <div class="text-h5 text-center font-weight-bold">{{ explorerPlayer.name }}</div>
                    <div class="text-subtitle-1 text-center text-grey">{{ explorerPlayer.position }}</div>
                  </v-col>
                  <v-col cols="12" md="8">
                    <v-list>
                      <v-list-item title="Nationality" :subtitle="explorerPlayer.nationality" prepend-icon="mdi-flag"></v-list-item>
                      <v-list-item title="Birth Date" :subtitle="explorerPlayer.birth_date" prepend-icon="mdi-calendar"></v-list-item>
                      <v-list-item title="Unified ID" :subtitle="explorerPlayer.id" prepend-icon="mdi-identifier"></v-list-item>
                    </v-list>
                  </v-col>
                </v-row>
                <v-divider class="my-4"></v-divider>
                <div class="text-subtitle-2 mb-2">Technical Unified Data</div>
                <div class="code-container unified-code">
                  <pre>{{ JSON.stringify(getCleanUnified(explorerPlayer), null, 2) }}</pre>
                </div>
              </v-card-text>
            </v-card>

            <v-card v-else variant="flat" class="bg-grey-lighten-4 d-flex align-center justify-center text-center pa-12" height="600">
              <div>
                <v-icon icon="mdi-soccer-field" size="100" color="grey-lighten-1" class="mb-4"></v-icon>
                <div class="text-h5 text-grey-darken-1">Select a Match or Player to explore</div>
                <p class="text-grey">Detailed unified records, lineups, and live timelines</p>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>

    <v-dialog v-model="dialog" max-width="1200px" scrollable>
      <v-card v-if="selectedItem">
        <v-card-title class="bg-primary text-white d-flex align-center">
          <span>Data Transformation & Pipeline Deep-Dive: {{ selectedItem.id }}</span>
          <v-spacer></v-spacer>
          <v-btn icon="mdi-close" variant="text" @click="dialog = false"></v-btn>
        </v-card-title>
        <v-card-text class="pa-0">
          <v-tabs v-model="activeTab" bg-color="primary">
            <v-tab value="raw">Raw vs Unified</v-tab>
            <v-tab value="mapping">Mapping Trace</v-tab>
            <v-tab value="docs">Pipeline Docs</v-tab>
          </v-tabs>

          <v-window v-model="activeTab" class="pa-4">
            <v-window-item value="raw">
              <v-card variant="outlined" class="mb-6 bg-blue-lighten-5 border-primary">
                <v-card-title class="text-subtitle-2 font-weight-bold">
                  <v-icon icon="mdi-matrix" start color="primary"></v-icon>
                  Consolidated Extraction Matrix (All Sources)
                </v-card-title>
                <v-card-text class="pa-0">
                  <v-table density="compact" class="bg-transparent">
                    <thead>
                      <tr>
                        <th>Source Provider</th>
                        <th>Data Harvested</th>
                        <th>Extraction Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(sourceData, sourceId) in selectedItem._raw_sources" :key="sourceId">
                        <td class="text-capitalize font-weight-bold">{{ sourceId }}</td>
                        <td>
                          <div class="d-flex flex-wrap gap-1 py-1">
                            <v-chip v-if="sourceId === 'statsbomb'" size="x-small">Tactical Events</v-chip>
                            <v-chip v-if="sourceId === 'statsbomb'" size="x-small">Competitions</v-chip>
                            <v-chip v-if="sourceId === 'opta'" size="x-small">Venue Info</v-chip>
                            <v-chip v-if="sourceId === 'opta'" size="x-small">Referees</v-chip>
                            <v-chip v-if="sourceId === 'sportradar'" size="x-small" color="success" variant="flat">Live Score</v-chip>
                            <v-chip v-if="sourceId === 'sportradar'" size="x-small">Betting Odds</v-chip>
                            <v-chip v-if="sourceId === 'wyscout'" size="x-small" color="info" variant="flat">Video Tags</v-chip>
                            <v-chip v-if="sourceId === 'wyscout'" size="x-small">UTC Norm</v-chip>
                          </div>
                        </td>
                        <td>
                          <v-icon icon="mdi-check-circle" color="success" size="small"></v-icon>
                          <span class="text-caption ml-1">Extracted</span>
                        </td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-card-text>
              </v-card>

              <v-row>
                <v-col cols="12" md="7">
                  <div class="text-subtitle-1 mb-2 font-weight-bold"><v-icon icon="mdi-database-import" start></v-icon> Source Raw Data (Inputs)</div>
                  <v-expansion-panels variant="accordion">
                    <v-expansion-panel v-for="(sourceData, sourceId) in selectedItem._raw_sources" :key="sourceId">
                      <v-expansion-panel-title class="text-capitalize">{{ sourceId }} Source Record</v-expansion-panel-title>
                      <v-expansion-panel-text>
                        <div class="code-container"><pre>{{ JSON.stringify(sourceData, null, 2) }}</pre></div>
                      </v-expansion-panel-text>
                    </v-expansion-panel>
                    <template v-if="selectedItem.events && selectedItem.events.length">
                      <v-expansion-panel class="mt-2 border-primary">
                        <v-expansion-panel-title class="bg-amber-lighten-5">
                          <v-icon icon="mdi-flash" start color="warning"></v-icon>
                          Event Transformation Sample
                        </v-expansion-panel-title>
                        <v-expansion-panel-text>
                          <v-row v-for="(event, idx) in selectedItem.events.slice(0, 2)" :key="idx" class="mb-4">
                            <v-col cols="12" sm="6">
                              <div class="text-caption font-weight-bold">RAW ({{ event.type }})</div>
                              <div class="code-container small-code"><pre>{{ JSON.stringify(event._raw_sources, null, 2) }}</pre></div>
                            </v-col>
                            <v-col cols="12" sm="6">
                              <div class="text-caption font-weight-bold">UNIFIED</div>
                              <div class="code-container unified-code small-code"><pre>{{ JSON.stringify(getCleanUnified(event), null, 2) }}</pre></div>
                            </v-col>
                          </v-row>
                        </v-expansion-panel-text>
                      </v-expansion-panel>
                    </template>
                  </v-expansion-panels>
                </v-col>
                <v-col cols="12" md="5">
                  <div class="text-subtitle-1 mb-2 font-weight-bold"><v-icon icon="mdi-vector-combine" start></v-icon> Unified Version (Output)</div>
                  <v-card variant="outlined" border color="success" class="code-card">
                    <v-card-text class="pa-0">
                      <div class="code-container unified-code"><pre>{{ JSON.stringify(getCleanUnified(selectedItem), null, 2) }}</pre></div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-window-item>

            <v-window-item value="mapping">
              <v-table density="compact">
                <thead>
                  <tr>
                    <th>Unified Property</th>
                    <th>Source Provider</th>
                    <th>Raw Path</th>
                    <th>Transformation Deep-Dive</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(map, prop) in selectedItem._mapping" :key="prop">
                    <td class="font-weight-bold text-primary">{{ prop }}</td>
                    <td><v-chip size="x-small" :color="map.source === 'statsbomb' ? 'green' : 'blue'">{{ map.source }}</v-chip></td>
                    <td><code>{{ map.path }}</code></td>
                    <td><div class="text-caption py-2">{{ map.explanation }}</div></td>
                  </tr>
                </tbody>
              </v-table>
            </v-window-item>

            <v-window-item value="docs">
              <div class="docs-container pa-4">
                <section class="mb-6">
                  <div class="text-h6 font-weight-bold color-primary mb-2">Architectural Logic (4-Way Aggregation)</div>
                  <p class="text-body-2">This pipeline resolves conflicts across 4 distinct paradigms using <strong>Weighted Source Priority</strong>. Because no single provider captures a football match perfectly, we merge data from:</p>
                </section>

                <v-row class="mb-6">
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="tonal" color="green" class="pa-3 h-100">
                      <div class="text-subtitle-2 font-weight-bold">StatsBomb</div>
                      <div class="text-caption">
                        <strong>Tactical Master:</strong> High-fidelity coordinates & xG.<br>
                        <strong>Trust:</strong> Names, tactical roles, event granularity.
                      </div>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="tonal" color="blue" class="pa-3 h-100">
                      <div class="text-subtitle-2 font-weight-bold">Opta</div>
                      <div class="text-caption">
                        <strong>Admin Master:</strong> Low-latency state transitions.<br>
                        <strong>Trust:</strong> Match minutes, DOBs, official status.
                      </div>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="tonal" color="orange" class="pa-3 h-100">
                      <div class="text-subtitle-2 font-weight-bold">Sportradar</div>
                      <div class="text-caption">
                        <strong>Betting Master:</strong> Ultra-fast live scores & basic state.<br>
                        <strong>Trust:</strong> Live scores & biometrics.
                      </div>
                    </v-card>
                  </v-col>
                  <v-col cols="12" sm="6" md="3">
                    <v-card variant="tonal" color="purple" class="pa-3 h-100">
                      <div class="text-subtitle-2 font-weight-bold">Wyscout</div>
                      <div class="text-caption">
                        <strong>Video Master:</strong> Human-tagged sub-events.<br>
                        <strong>Trust:</strong> Event outcomes, UTC timestamps.
                      </div>
                    </v-card>
                  </v-col>
                </v-row>

                <section class="mb-6">
                  <div class="text-h6 font-weight-bold mb-2">Transformation Stages</div>
                  <v-list density="compact">
                    <v-list-item title="1. Normalization" subtitle="Translating disparate formats (e.g., Opta IDs, Wyscout UTC dates, StatsBomb grids)."></v-list-item>
                    <v-list-item title="2. Reconciliation" subtitle="Matching 4 separate IDs (Opta m123 = SB 5503 = SR 999 = WY 500) via a master graph."></v-list-item>
                    <v-list-item title="3. Arbitration" subtitle="Selecting the 'winner' for each property based on the source's designated expertise."></v-list-item>
                    <v-list-item title="4. Aggregation" subtitle="Building the final USO (Unified Sports Object) with full provenance trace."></v-list-item>
                  </v-list>
                </section>
              </div>
            </v-window-item>
          </v-window>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="grey-darken-1" variant="text" @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="error" color="error" timeout="3000">{{ errorMessage }}</v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';

const matches = ref([]);
const players = ref([]);
const loading = ref(false);
const error = ref(false);
const errorMessage = ref('');

const mainTab = ref('overview');
const dialog = ref(false);
const activeTab = ref('raw');
const selectedItem = ref(null);
const playerSearch = ref('');

const explorerType = ref(null);
const explorerMatch = ref(null);
const explorerPlayer = ref(null);
const explorerSubTab = ref('lineups');
const eventSearch = ref('');
const eventTypeFilter = ref('All');

const filteredEvents = computed(() => {
  if (!explorerMatch.value || !explorerMatch.value.events) return [];
  let events = explorerMatch.value.events;
  
  if (eventTypeFilter.value !== 'All') {
    events = events.filter(e => {
      if (eventTypeFilter.value === 'Goal') {
        return e.type === 'Shot' && e.outcome === 'Goal';
      }
      if (eventTypeFilter.value === 'Foul Committed') {
        return e.type === 'Foul Committed';
      }
      return e.type === eventTypeFilter.value;
    });
  }
  return events;
});

const headers = [
  { title: 'Date', key: 'match_date', align: 'start' },
  { title: 'Competition', key: 'competition' },
  { title: 'Home', key: 'home_team_id' },
  { title: 'Away', key: 'away_team_id' },
  { title: 'Score', key: 'score', align: 'center' },
  { title: 'Status', key: 'status', align: 'center' },
  { title: 'Sources', key: 'provenance' },
  { title: 'Actions', key: 'actions', align: 'end' },
];

const playerHeaders = [
  { title: 'Name', key: 'name', align: 'start' },
  { title: 'Nationality', key: 'nationality' },
  { title: 'Position', key: 'position' },
  { title: 'Actions', key: 'actions', align: 'end' },
];

const eventHeaders = [
  { title: 'Min', key: 'minute', width: '60px' },
  { title: 'Type', key: 'type' },
  { title: 'Player', key: 'player_id' },
  { title: 'Team', key: 'team_id' },
  { title: 'Outcome', key: 'outcome' },
];

const getEventColor = (type) => {
  const colors = {
    'Shot': 'error',
    'Pass': 'success',
    'Goal': 'warning',
    'Foul Committed': 'deep-orange',
    'Ball Recovery': 'indigo',
    'Duel': 'blue-grey'
  };
  return colors[type] || 'grey';
};

const fetchMatches = async () => {
  loading.value = true;
  try {
    const response = await api.getMatches();
    matches.value = response.data.items;
  } catch (err) {
    errorMessage.value = 'Failed to load match data.';
    error.value = true;
  } finally {
    loading.value = false;
  }
};

const fetchPlayers = async () => {
  try {
    const response = await api.getPlayers();
    players.value = response.data.items;
  } catch (err) {}
};

const showTransformation = (item) => {
  selectedItem.value = item;
  dialog.value = true;
};

const getCleanUnified = (item) => {
  if (!item) return {};
  const clean = { ...item };
  delete clean._raw_sources;
  delete clean._mapping;
  delete clean._provenance;
  if (clean.events) {
    clean.events = clean.events.map(e => {
      const ec = { ...e };
      delete ec._raw_sources;
      delete ec._mapping;
      return ec;
    });
  }
  return clean;
};

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
  });
};

onMounted(() => {
  fetchMatches();
  fetchPlayers();
});
</script>

<script>
export default {
  name: 'MatchDashboard'
}
</script>

<style scoped>
.gap-1 { gap: 4px; }
.code-container {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Fira Code', monospace;
  font-size: 0.85rem;
}
.unified-code { background-color: #e8f5e9; }
.small-code { font-size: 0.75rem; max-height: 250px; }
.code-card { border-width: 2px; }
pre { white-space: pre-wrap; word-wrap: break-word; }
.docs-container { max-height: 600px; overflow-y: auto; }
.explorer-sidebar { border-right: 1px solid #e0e0e0; height: calc(100vh - 150px); overflow-y: auto; }
.explorer-list { height: 100%; }
.sticky-header { position: sticky; top: 0; z-index: 2; }
.border-bottom { border-bottom: 1px solid #eee; }
</style>
