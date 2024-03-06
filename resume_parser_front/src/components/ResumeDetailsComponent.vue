<!-- eslint-disable -->
<template>
  <v-container fluid id="container">
    <v-row>
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title style="height: 100px; position: relative" class="grey lighten-5">
            <v-badge bordered color="blue" icon="mdi-check" :value="checked"
              ><h2 class="blue--text text--darken-4">Détails CV</h2></v-badge
            >
            <v-spacer></v-spacer>
            <div class="text-center">
              <div class="text-center">
                <v-btn class="mx-2" fab dark large color="red darken-2" @click="reset()"
                  ><v-icon dark> mdi-close </v-icon></v-btn
                >
                <v-btn class="mx-2" fab dark large color="primary" @click="reExtract()"
                  ><v-icon dark> mdi-text-box-search </v-icon></v-btn
                >
                <v-btn class="mx-2" fab dark large color="warning" @click="update()"
                  ><v-icon dark> mdi-check </v-icon></v-btn
                >
              </div>
              <v-dialog v-model="Updated" width="500">
                <v-card>
                  <v-card-title class="text-h5 grey lighten-2">
                    Modification(s) effectuée(s) avec succée</v-card-title
                  >
                  <br />
                  <v-card-text> Voulez Vous effectuer d'autre(s) modification ? </v-card-text>
                  <v-divider></v-divider>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" text @click="Updated = false"> Oui </v-btn>
                    <v-btn color="primary" text @click="reroute()"> Non </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
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
            </div>
          </v-card-title>
          <v-divider class="mt-6 mx-4"></v-divider>
          <br />

          <v-container id="scroll-target" style="height: 1000px" class="overflow-y-auto">
            <v-form ref="form" v-model="valid" lazy-validation v-if="currentResume">
              <h3 class="blue--text text--darken-3">Valider</h3>
              <v-switch v-model="checked" color="primary"></v-switch>
              <h3 class="blue--text text--darken-3">Détails personnels</h3>
              <br />
              <v-spacer></v-spacer>

              <v-row>
                <v-col cols="4" md="8">
                  <v-text-field
                    v-model="name"
                    :rules="nameRules"
                    label="Nom & Prénom"
                    :counter="25"
                    required
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="4" md="8">
                  <v-text-field
                    v-model="email"
                    :rules="emailRules"
                    label="E-mail"
                    required
                  ></v-text-field>
                </v-col>
              </v-row>

              <v-row>
                <v-col cols="4" md="8">
                  <v-text-field
                    v-model="phone"
                    :rules="telRules"
                    label="Téléphone"
                    :counter="15"
                    required
                  ></v-text-field>
                </v-col>
              </v-row>
              <v-row>
                <v-col cols="4" md="8">
                  <v-text-field v-model="linkedin" label="Linkedin"></v-text-field>
                </v-col>
              </v-row>
              <v-divider class="mt-6 mx-4"></v-divider>
              <h3 class="blue--text text--darken-3">Profil</h3>
              <v-spacer></v-spacer>
              <v-row>
                <v-col cols="6" md="8">
                  <br /><br />
                  <div>
                    <p class="blue--text text--darken-4">Education</p>
                    <div>
                      <v-combobox
                        v-model="university"
                        chips
                        clearable
                        label="Education"
                        multiple
                        solo
                      >
                        <template v-slot:selection="{ attrs, item, select, selected }">
                          <v-chip
                            v-if="item != ''"
                            v-bind="attrs"
                            :input-value="selected"
                            close
                            text-color="white"
                            color="blue darken-1"
                            @click="select"
                            @click:close="removeEducation(item)"
                          >
                            {{ item }}
                            &nbsp;
                          </v-chip>
                        </template>
                      </v-combobox>
                    </div>
                  </div>
                </v-col>
                <v-col cols="6" md="8">
                  <div>
                    <p class="blue--text text--darken-4">Niveau/Diplome</p>
                    <div>
                      <v-combobox
                        v-model="degree"
                        chips
                        clearable
                        label="Niveau/Diplome"
                        multiple
                        solo
                      >
                        <template v-slot:selection="{ attrs, item, select, selected }">
                          <v-chip
                            v-if="item != ''"
                            v-bind="attrs"
                            :input-value="selected"
                            close
                            text-color="white"
                            color="blue darken-1"
                            @click="select"
                            @click:close="removeDegree(item)"
                          >
                            {{ item }}
                            &nbsp;
                          </v-chip>
                        </template>
                      </v-combobox>
                    </div>
                  </div>
                </v-col>
                <v-col cols="4" md="8">
                  <div>
                    <p class="blue--text text--darken-4">Poste(s) occupée(s)</p>
                    <div>
                      <v-combobox
                        v-model="designition"
                        chips
                        clearable
                        label="Poste(s) occupée(s)"
                        multiple
                        solo
                      >
                        <template v-slot:selection="{ attrs, item, select, selected }">
                          <v-chip
                            v-if="item != ''"
                            v-bind="attrs"
                            :input-value="selected"
                            close
                            text-color="white"
                            color="blue darken-1"
                            @click="select"
                            @click:close="removeDesi(item)"
                          >
                            {{ item }}
                            &nbsp;
                          </v-chip>
                        </template>
                      </v-combobox>
                    </div>
                  </div>
                </v-col>
              </v-row>
              <v-row>
                <br /><br />
                <v-col cols="4" md="8">
                  <div>
                    <p class="blue--text text--darken-4">Expérience professionelle chez</p>
                    <div>
                      <v-combobox
                        v-model="companies"
                        chips
                        clearable
                        label="Expérience professionelle"
                        multiple
                        solo
                      >
                        <template v-slot:selection="{ attrs, item, select, selected }">
                          <v-chip
                            v-bind="attrs"
                            v-if="item != ''"
                            :input-value="selected"
                            close
                            text-color="white"
                            color="blue"
                            @click="select"
                            @click:close="removeComp(item)"
                          >
                            {{ item }}
                            &nbsp;
                          </v-chip>
                        </template>
                      </v-combobox>
                    </div>
                  </div>
                </v-col>
                <v-col cols="4" md="8">
                  <p class="blue--text text--darken-4">Total expérience</p>
                  <v-menu
                    v-model="menu"
                    :close-on-content-click="false"
                    :nudge-width="200"
                    offset-x
                  >
                    <template v-slot:activator="{ on }">
                      <v-btn icon x-large v-on="on">
                        <v-avatar color="light-blue " size="62">
                          <span class="white--text text-h5">{{ total_exp }}</span>
                        </v-avatar>
                      </v-btn>
                    </template>
                    <v-card>
                      <v-card-title>Total expérience</v-card-title>
                      <v-card-text>
                        <v-text-field
                          label="Total expérience"
                          v-model="exp"
                          required
                        ></v-text-field>
                      </v-card-text>
                      <v-card-actions>
                        <v-spacer></v-spacer>
                        <v-btn
                          text
                          @click="
                            {
                              menu = false;
                              exp = total_exp;
                            }
                          "
                        >
                          Annuler
                        </v-btn>
                        <v-btn color="primary" text @click="UpdateExp()"> Sauvegarder </v-btn>
                      </v-card-actions>
                    </v-card>
                  </v-menu>
                </v-col>
                <br /><br />
                <v-col cols="12" md="12">
                  <div>
                    <v-menu
                      v-model="menu2"
                      :close-on-content-click="false"
                      :nudge-width="200"
                      top
                      offset-x
                    >
                      <template v-slot:activator="{ on }">
                        <p class="blue--text text--darken-4">
                          Compétences
                          <v-btn
                            class="mx-2"
                            v-on="on"
                            fab
                            dark
                            small
                            color="blue darken-2"
                            top
                            right
                            @click="getSkillsDB()"
                          >
                            <v-icon>mdi-plus</v-icon>
                          </v-btn>
                        </p>
                      </template>
                      <v-card>
                        <v-card-title>Ajouter compétence</v-card-title>
                        <v-card-text>
                          <v-text-field
                            v-model="skill"
                            label="Valeur"
                            clearable
                            required
                          ></v-text-field>
                          <v-select
                            v-model="type"
                            :items="['Hard Skill', 'Soft Skill', 'Certification']"
                            label="Type"
                            dense
                            required
                          ></v-select>
                        </v-card-text>
                        <v-card-actions>
                          <v-spacer></v-spacer>
                          <v-btn
                            text
                            @click="
                              {
                                menu2 = false;
                                skill = '';
                                type = null;
                              }
                            "
                          >
                            Quitter
                          </v-btn>
                          <v-btn color="primary" text @click="AddSkill()"> Sauvegarder </v-btn>
                        </v-card-actions>
                      </v-card>
                    </v-menu>
                    <div>
                      <br />
                      <v-combobox
                        v-model="skills"
                        :items="[...skills, ...AllSkills]"
                        :item-text="(item) => item.value"
                        :menu-props="{ bottom: true, right: true, offsetX: true }"
                        chips
                        clearable
                        label="Competences"
                        multiple
                        append-icon
                        solo
                      >
                        <template v-slot:selection="{ attrs, item, select, selected }"
                          ><v-tooltip bottom>
                            <template #activator="{ on }">
                              <v-chip
                                v-bind="attrs"
                                v-on="on"
                                :input-value="selected"
                                close
                                text-color="white"
                                :color="chipColor(item.score)"
                                @click="find(item.value)"
                                @click:close="removeSkill(item)"
                              >
                                {{ item.value }}
                                &nbsp;
                              </v-chip>
                            </template>
                            <span>{{ item.type }}</span>
                            <br />
                            <span>{{ item.score }}</span>
                          </v-tooltip>
                        </template>
                      </v-combobox>
                    </div>
                  </div>
                </v-col>
              </v-row>
            </v-form>
          </v-container>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <iframe id="iframe" height="100%" width="100%" :src="`${source}`" title="resume"></iframe>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
/* eslint-disable */
import axios from "axios";

export default {
  data: () => ({
    valid: true,
    nameRules: [(v) => !!v || "Name is required"],
    emailRules: [
      (v) => !!v || "E-mail is required",
      (v) => /.+@.+\..+/.test(v) || "E-mail must be valid",
    ],
    telRules: [
      (v) => !!v || "Phone number is required",
      (v) => (v && v.length >= 8) || "Phone number must be at least 8 characters",
    ],
    name: "",
    email: "",
    phone: "",
    linkedin: "",
    university: [],
    degree: [],
    designition: [],
    companies: [],
    total_exp: 0,
    skills: [],
    checked: false,
    file: null,
    filename: "",
    source: null,
    currentResume: null,
    AllSkills: [],
    exp: 0,
    menu: false,
    dialog: false,
    menu2: false,
    skill: null,
    type: null,
    Updated: false,
  }),

  methods: {
    validate() {},
    reset() {
      this.getData();
    },
    getData() {
      const path = "http://localhost:5000/fetchResume/" + this.$route.params.id;
      axios
        .get(path)
        .then((res) => {
          console.log(res.data.status);
          this.currentResume = res.data.data[0].id;
          this.name = res.data.data[0].name;
          this.email = res.data.data[0].email;
          this.phone = res.data.data[0].phone;
          this.linkedin = res.data.data[0].linkedin;
          this.university = res.data.data[0].university.slice(2, -2).split("', '");
          this.degree = res.data.data[0].degree.slice(2, -2).split("', '");
          this.designition = res.data.data[0].designition.slice(2, -2).split("', '");
          this.companies = res.data.data[0].companies.slice(2, -2).split("', '");
          this.total_exp = res.data.data[0].exp;
          this.file = res.data.data[0].file_path.split("\\");
          this.skills = res.data.skills;
          this.checked = res.data.data[0].checked;
          this.source = "http://localhost:33333/" + this.file[this.file.length - 1];
          this.filename = this.file[this.file.length - 1];
          this.exp = this.total_exp;
          console.log(this.source);
          console.log(this.currentResume);
          if (this.university[0] == "") this.university = [];
          if (this.degree[0] == "") this.degree = [];
          if (this.designition[0] == "") this.designition = [];
          if (this.companies[0] == "") this.companies = [];
          this.getSkillsDB();
        })
        .catch((error) => {
          console.error(error);
        });
    },
    chipColor(value) {
      return value >= 0.9 ? "blue darken-4" : "blue lighten-1";
    },
    find(searched) {
      var inputText = document.getElementById("container");
      if (searched !== "") {
        let text = document.getElementById("iframe").innerHTML;
        let re = new RegExp(searched, "g"); // search for all instances
        let newText = text.replace(re, `<mark>${searched}</mark>`);
        document.getElementById("iframe").innerHTML = newText;
      }
    },
    removeSkill(item) {
      this.skills.splice(this.skills.indexOf(item), 1);
    },
    see(value) {
      console.log(value);
    },
    removeComp(item) {
      this.companies.splice(this.companies.indexOf(item), 1);
    },
    removeDesi(item) {
      this.designition.splice(this.designition.indexOf(item), 1);
    },
    removeDegree(item) {
      this.degree.splice(this.degree.indexOf(item), 1);
    },
    removeEducation(item) {
      this.university.splice(this.university.indexOf(item), 1);
    },
    update() {
      const path = "http://localhost:5000/UpdateResume/" + this.$route.params.id;
      axios
        .put(path, {
          data: {
            name: this.name,
            email: this.email,
            phone: this.phone,
            linkedin: this.linkedin,
            university: this.university,
            degree: this.degree,
            designition: this.designition,
            companies: this.companies,
            exp: this.total_exp,
            checked: this.checked,
          },
          skills: {
            skills: this.skills,
          },
        })
        .then((res) => {
          console.log(res);
          this.Updated = true;
          this.getData();
        })
        .catch((error) => {
          console.error(error);
          this.getData();
        });
    },
    reExtract() {
      this.dialog = true;
      const path =
        "http://localhost:5000/Re-extract/" + this.$route.params.id + "/" + this.filename;
      axios
        .get(path)
        .then((res) => {
          console.log(res);
          this.dialog = false;
          this.$router.push("/Details/" + res.data.new_id);
          this.getData();
        })
        .catch((error) => {
          console.error(error);
        });
    },
    UpdateExp() {
      this.total_exp = this.exp;
      this.menu = false;
    },
    getSkillsDB() {
      const path = "http://localhost:5000/fetchAllSkills";
      axios
        .get(path)
        .then((res) => {
          console.log(res);
          this.AllSkills = res.data.data;
        })
        .catch((error) => {
          console.error(error);
        });
    },
    AddSkill() {
      if (this.type != null && this.value != "") {
        this.skills.push({
          resume_id: this.currentResume,
          doc_node_id: "[]",
          score: 2,
          type: this.type,
          value: this.skill,
        });
      }
      this.type = null;
      this.value = "";
    },
    findType(value) {
      var type = "";
      this.AllSkills.forEach((e) => {
        if (e.value == value) type = e.type;
      });
      return type;
    },
    reroute() {
      this.$router.push("/Resumes");
    },
  },
  created() {
    this.getData();
    this.validate();
    this.reset();
    this.chipColor(value);
    this.find(value);
    this.removeSkill(item);
    this.see(value);
    this.removeComp(item);
    this.removeDegree(item);
    this.removeDesi(item);
    this.removeEducation(item);
    this.update();
    this.UpdateExp();
    this.getSkillsDB();
    this.findType();
  },
};
</script>
<style>
.highlight {
  background-color: yellow;
}
</style>
