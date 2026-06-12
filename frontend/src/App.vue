<template>
  <v-app>
    <v-app-bar color="primary" elevation="1">
      <v-app-bar-title>Football Data Platform</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-btn icon="mdi-github" href="https://github.com" target="_blank"></v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-4">
      <MatchDashboard />
    </v-main>

    <v-footer app border>
      <span class="text-caption text-grey">
        DataTransformerAggregator &copy; {{ new Date().getFullYear() }} - Portfolio Demo
      </span>
    </v-footer>
  </v-app>
</template>

<script setup>
import MatchDashboard from './components/MatchDashboard.vue'
</script>

<style>
#app {
  font-family: 'Roboto', sans-serif;
}
</style>
