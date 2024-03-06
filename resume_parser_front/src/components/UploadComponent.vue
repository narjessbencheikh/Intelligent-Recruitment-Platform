<template>
  <div>
    <div>
      <vueDropzone
        ref="myVueDropzone"
        id="myVueDropzone"
        @vdropzone-success="upload_complete"
        @vdropzone-removed-file="cancel_upload"
        :options="dropzoneOptions"
        :useCustomSlot="true"
      >
        <div class="dropzone-custom-content">
          <h3 class="dropzone-custom-title">Glissez vos documents ici !</h3>
          <div class="subtitle">...Ou selectionnez vos documents à partir de votre machine</div>
        </div>
      </vueDropzone>
      <div class="text-center">
        <v-btn class="mx-2" fab dark large color="red darken-2" @click="removeAllFiles()"
          ><v-icon dark> mdi-close </v-icon></v-btn
        >
        <v-btn class="mx-2" fab dark large color="primary" @click="Extract_file"
          ><v-icon dark> mdi-text-box-search </v-icon></v-btn
        >
      </div>
      <br />
      <div class="text-center">
        <v-dialog v-model="dialog" hide-overlay persistent width="300">
          <v-card color="primary" dark>
            <br />
            <v-card-text> Veuillez patientez SVP... </v-card-text>
            <br />
            <v-card-text
              ><v-progress-linear indeterminate color="white" class="mb-0"></v-progress-linear
            ></v-card-text>
            <br />
          </v-card>
        </v-dialog>
        <v-dialog v-model="exception" width="500">
          <v-card>
            <v-card-title class="text-h5 grey lighten-2"> Echec d'execution </v-card-title>
            <br />
            <v-card-text> {{ Exception_msg }} </v-card-text>
            <v-card-text> Veuillez re-télécharger vos documents </v-card-text>

            <v-divider></v-divider>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="primary" text @click="exception = false"> ok </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
// TODO: convert files to pdf upon upload !!
import vue2Dropzone from "vue2-dropzone";
import "vue2-dropzone/dist/vue2Dropzone.min.css";
import axios from "axios";

export default {
  components: {
    vueDropzone: vue2Dropzone,
  },
  data: function () {
    return {
      dropzoneOptions: {
        url: "http://localhost:5000/upload",
        addRemoveLinks: true,
        thumbnailWidth: 150,
        maxFilesize: 2,
        maxFiles: 10,
      },
      dialog: false,
      exception: false,
      Exception_msg: "",
      done: true,
    };
  },
  methods: {
    removeAllFiles() {
      this.$refs.myVueDropzone.removeAllFiles();
    },
    upload_complete(file, response) {
      console.log("uploaded");
      console.log(file["name"]);
    },
    cancel_upload(file, error, xhr) {
      console.log("cancelled upload");
      console.log(file["name"]);
      const path = "http://localhost:5000/removeFile";
      axios
        .delete(path, {
          data: {
            cancel_file: file["name"],
          },
        })
        .then((res) => {
          console.log(res);
        })
        .catch((error) => {
          console.error(error);
        });
    },
    Extract_file() {
      this.dialog = true;
      const path = "http://localhost:5000/extract";
      axios
        .get(path)
        .then((res) => {
          console.log(res);
          this.dialog = false;
          this.removeAllFiles();
          if (res.data.status == "failed") {
            this.Exception_msg = res.data.status;
            this.exception = true;
          }
          this.$router.push("/Resumes");
        })
        .catch((error) => {
          console.error(error);
          this.dialog = false;
          this.Exception_msg = error + "";
          this.exception = true;
        });
    },
  },
  created() {
    this.removeAllFiles();
    this.upload_complete(file, response);
    this.cancel_upload(file, error, xhr);
    this.Extract_file();
  },
};
</script>
