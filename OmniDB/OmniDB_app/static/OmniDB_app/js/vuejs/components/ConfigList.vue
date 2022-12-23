<template>
      <div class="row form-group">
      <div class="col-3 mr-auto">
        <form method="get" class="form" role="search">
          <label class="sr-only" for="selectServer">Search</label>
          <div class="input-group">
            <input v-model="query_filter" class="form-control" id="inputSearchSettings" name="filter" placeholder="Find in settings">
            <span class="input-group-append">
              <!-- <button v-if="!!query_filter" class="btn btn-outline-secondary" id="buttonResetSearch" @click.prevent="clearFilter">
                <i class="fa fa-fw fa-times"></i>
            </button> -->
              <button type="submit" class="btn btn-secondary" id="buttonSearchSettings" @click.prevent="getConfiguration">
                <i class="fa fa-fw fa-search"></i>
              </button>
            </span>
          </div>
        </form>
      </div>

      <div class="col-7">
        <label class="sr-only" for="selectConfCat">Category</label>
        <div class="input-group">
            <div class="input-group-prepend">
              <div class="input-group-text">
                Category
              </div>
              <select class="form-control" id="selectConfCat" :disabled="!!query_filter" v-model="selected">
                <option v-for="cat in categories" :value="cat">{{ cat }}</option>
              </select>
            </div>
        </div>
      </div>
    </div>
    <div v-if="hasResult" class="row">
      <div class="col-12"><p>No results found...</p></div>
    </div>
    <div v-else class="row">
      <div class="col-12">
        <div class="card" v-for="setting_group in currentResult">
          <div class="card-header">
          {{ setting_group.category }}
          </div>
          <div class="card-body">
            <form role="form" method="post">
              <table class="table table-sm">
                <tr v-for="setting_row in setting_group.rows">
                  <td class="badge-settings">
                    <span class="title-setting">
                    {{ setting_row.name }}
                    </span>
                    <p class="text-muted mb-0 small">
                      {{ setting_row.desc }}</p>
                  </td>
                  <td class="input-setting">
                    <div class="text-center" v-if="setting_row.vartype === 'bool'">
                      <input type="checkbox" data-toggle="toggle" data-size="mini" data-onstyle="success" data-offstyle="danger"
                      :id="`select${setting_row.name}`"  :checked="setting_row.setting === 'on'"/>
                      <input :id="`hidden${setting_row.name}`" type="hidden" :name="setting_row.name" value="on"/>
                      <!-- it should be here ^ 
                        id="select{{setting_row['name']}}" {% if setting_row['setting'] == 'on' %}checked{% end %}-->
                        <!-- <input id="hidden{{setting_row['name']}}" type="hidden" name="{{setting_row['name']}}" value="{% if setting_row['setting'] == 'on' %}on{%else%}off{% end %}" /> -->
                    </div>
                    <!-- elif setting_row['vartype'] == 'enum'-->
                    <select v-else-if="setting_row.vartype === 'enum'" class="form-control form-control-sm" :name="setting_row.name" :id="`select${setting_row.name}`">
                      <option v-for="v in setting_row.enumvals" :value="v">{{ v }}</option>
                      <!-- {% for v in setting_row['enumvals'][1:-1].split(',') %}
                      <option value="{{v}}" {% if (v.startswith('"') and v.endswith('"') and setting_row['setting'] == v[1:-1]) or setting_row['setting'] == v %} selected="selected"{% end %}>
                        {{v}}
                      </option>
                      {% end %} -->
                    </select>
                    <!-- else-->
                    <input v-else data-toggle="popover" data-trigger="hover" data-placement="top" data-html="true" type="text" :name="setting_row.name" :id="`input${setting_row.name}`" 
                   :placeholder="setting_row.name" :value="setting_row.setting ? setting_row.setting_raw : ''"
                    :data-content='`<table>
                                    <tr>
                                      <td>Type:</td>
                                      <td><b>${ setting_row.vartype }</b></td>
                                    </tr>
                                    <tr>
                                      <td>Unit:</td>
                                      <td><b>${ setting_row.unit }</b></td>
                                    </tr>
                                    <tr>
                                      <td>Minimum:</td>
                                      <td><b>${setting_row.min_val}</b></td>
                                    </tr>
                                    <tr>
                                      <td>Maximum:</td>
                                      <td><b>${setting_row.max_val}
                                      </b>
                                      </td>
                                    </tr>
                                  </table>`'
                                  >
                    <!-- end -->
                    <button v-if="setting_row.setting != setting_row.boot_val" type="button" class="btn btn-link" :id="`buttonResetDefault_${setting_row.name}`" data-toggle="popover" data-trigger="hover" data-placement="right" :title="setting_row.name" data-html="true" :data-content="`Reset to: ${setting_row.boot_val}`">
                      <span class="fa fa-undo" aria-hidden="true"></span>
                      Reset to default
                    </button>
                    <!-- {% end %} -->
                  </td>
                </tr>
              </table>
              <div class="row">
                <div class="col-12 text-center">
                  <button type="submit" class="btn btn-sm btn-success" @click.prevent="logging">Save and reload configuration</button>
                </div>
              </div>
            </form>
          </div>
        </div>
        <!-- end -->
      </div>
    </div>
</template>

<script>

export default {
    data() {
        return {
          query_filter: '',
          data: '',
          selected: '',
          categories: ''
        }
      },
      computed: {
        currentResult() {
          if (!!this.data) {
            if (!this.query_filter) {
            return this.data.filter((item) => item.category.match(this.selected))
            } else {
              return this.data.map((element) => {
                const elementCopy = {...element};
                const rows = elementCopy.rows.filter((row) => row.name.includes(this.query_filter));
                  return {...elementCopy, rows: rows}
                }).filter((element) => !!element.rows.length);
            }
          }
        },
        hasResult() {
          return !this.currentResult?.length
        }
      },
      methods: {
        getConfiguration() {
          axios({
            method: 'post',
            url: '/configuration/',
            data: {
              data: JSON.stringify({
                "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
                "p_tab_id": window.v_connTabControl.selectedTab.id,
                "query_filter": this.query_filter
              })
            }
          })
          .then((response) => {
            console.log(response)
            this.data = response.data
            // this.categories = this.data.map(function({category, rows}) { return category})
            this.categories = this.data.map(x => x.category)
            // this.categories = Object.keys(this.data)

            this.selected = this.categories[0]
          })
          .catch((error) => {
            this.data = ''
            console.log(error)
          })
        },
        getCategories() {
          axios({method: 'post',
          url: '/configuration/categories/',
          data: { 
            data: JSON.stringify({
            "p_database_index": window.v_connTabControl.selectedTab.tag.selectedDatabaseIndex,
            "p_tab_id": window.v_connTabControl.selectedTab.id,
          })
          },
        })
          .then((response) => {
            console.log(response)
            this.categories = response.data.data
            this.selected = this.categories[0]
          })
          .catch((error) => {
            console.log(error)
          })
        },
      },
      mounted() {
          this.getConfiguration();
      },
}
</script> 

<style>
.input-setting {
  width: 20%;
}
</style>