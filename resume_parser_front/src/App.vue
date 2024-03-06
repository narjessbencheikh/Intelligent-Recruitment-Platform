<!-- eslint-disable -->
<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <div class="d-flex align-center">
        <h1  class="mr-2">Analyseur de CVs</h1>
      </div>

      <v-spacer></v-spacer>

      <v-btn icon @click="upload()">
        <v-icon>mdi-file-upload</v-icon>
      </v-btn>
      <v-btn icon @click="reroute()">
        <v-icon>mdi-table-account </v-icon>
      </v-btn>
      <br />
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
/* eslint-disable */
export default {
  name: "App",

  data: () => ({
    //
  }),
  methods: {
    reroute() {
      this.$router.push("/Resumes");
    },
    upload() {
      this.$router.push("/Upload");
    },
  },
};
</script>
