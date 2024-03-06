<!-- eslint-disable -->
<template>
  <v-container fluid style="height: 1000px" class="overflow-y-auto">
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            Liste des CVs
            <v-spacer></v-spacer>
            <v-text-field
              v-model="search"
              append-icon="mdi-magnify"
              label="Recherche"
              single-line
              hide-details
            ></v-text-field>
          </v-card-title>
          <v-data-table
            v-model="selected"
            :headers="headers"
            :items="resumes"
            :search="search"
            :single-select="singleSelect"
            item-key="id"
            show-select
            class="elevation-1"
          >
            <template v-slot:[`item.action`]="{ /* eslint-disable */ item }">
              <v-btn color="primary" fab small dark @click="goToDetails(item.id)"
                ><v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn color="secondary" fab small dark @click="viewFile(item.file_path)"
                ><v-icon>mdi-eye</v-icon>
              </v-btn>
            </template>
            <template v-slot:item.checked="{ item }">
              <v-chip :color="getColor(item.checked)" dark>
                {{ status(item.checked) }}
              </v-chip>
            </template>
          </v-data-table>

          <v-fab-transition v-if="selected !== []">
            <v-btn @click="remove()" color="red darken-1" dark absolute bottom left fab>
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </v-fab-transition>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <iframe height="100%" width="100%" :src="`${source}`"></iframe>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
/* eslint-disable */
import axios from "axios";
import VuePdfEmbed from "vue-pdf-embed/dist/vue2-pdf-embed";

export default {
  data() {
    return {
      resumes: [],
      singleSelect: false,
      selected: [],
      headers: [
        {
          text: "Nom & Prénom",
          align: "start",
          value: "name",
        },
        { text: "Etat", value: "checked" },
        { text: "Email", value: "email" },
        { text: "Téléphone", value: "phone" },
        { text: "", value: "action" },
      ],
      search: "",
      dragover: false,
      uploadedFiles: [],
      source: "https://cdn.vuetifyjs.com/docs/images/logos/vuetify-logo-light-atom.svg",
      list: [],
    };
  },
  components: {
    VuePdfEmbed,
  },

  methods: {
    getresumes() {
      const path = "http://localhost:5000/fetchAll";
      axios
        .get(path)
        .then((res) => {
          this.resumes = res.data.resumes;
          console.log(this.resumes);
        })
        .catch((error) => {
          console.error(error);
        });
    },
    goToDetails(id) {
      this.$router.push("/Details/" + id);
    },
    viewFile(file_path) {
      this.list = file_path.split("\\");
      console.log(this.list);
      this.source = "http://localhost:33333/" + this.list[this.list.length - 1];
      console.log(this.source);
    },
    reroute() {
      this.$router.push("/Upload");
    },
    remove() {
      const path = "http://localhost:5000/DeleteResume/";
      this.selected.forEach((item) =>{
        console.log(item.id);
        axios
          .delete(path + item.id)
          .then((res) => {
            console.log(res);
            this.getresumes();
          })
          .catch((error) => {
            console.error(error);
          })
      }
      
      );

    },
    getColor(value){
      return value == true ? "blue darken-4" : "blue lighten-1";
    },
    status(value){
      return value == true ? "Validé" : "Non-validé"
    }


  },
  created() {
    this.getresumes();
    this.goToDetails(id);
    this.viewFile(file_path);
    this.remove();
    this.getColor(value);
    this.status(value);
  },
};
</script>
