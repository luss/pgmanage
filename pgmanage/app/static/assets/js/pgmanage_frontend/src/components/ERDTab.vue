<template>
  <div style="width: 100%; height: 100vh; visibility: hidden" ref="cyContainer"></div>
</template>

<script>
import axios from 'axios'
import cytoscape from 'cytoscape';
import nodeHtmlLabel from 'cytoscape-node-html-label'

// TODO: add fit/pan/zoom buttons
// TODO: handlecontainer resize

export default {
  name: "ERDTab",
  props: {
    schema: String,
    tab_id: String,
    database_index: Number,
    database_name: String,
  },
  setup(props) {
  },
  data() {
    return {
        nodes: [],
        edges: [],
        cy: {}
    };
  },
  mounted() {
    this.loadSchemaGraph()
  },
  methods: {
    loadSchemaGraph() {
      axios.post('/draw_graph/', {
        database_index: this.database_index,
        tab_id: this.tab_id,
        schema: this.schema,
      })
      .then((response) => {
        this.nodes = response.data.v_data.nodes.map((node) => (
          {
            data: {
              id: node.id,
              label: node.label,
              columns: node.columns.map((column) => (
                {
                  name: column.name,
                  type: this.shortDataType(column.type),
                  cgid: column.cgid,
                  is_pk: column.is_pk,
                  is_fk: column.is_fk,
                  is_highlighed: false
                }
              )),
              type: 'table'
            },
            position: {},
            classes: 'group' + node.group
          }
        ))

        this.edges = response.data.v_data.edges.map((edge) => (
          {
            data: {
              source: edge.from,
              target: edge.to,
              source_col: edge.from_col,
              target_col: edge.to_col,
              label: edge.label,
              cgid: edge.cgid
            }
          }
        ))
      })
      .then(() => { this.initGraph() })
      .catch((error) => {
        console.log(error)
      })
    },
    shortDataType(typename) {
      const TYPEMAP = {
        'character varying': 'varchar',
        'timestamp with time zone': 'timestamptz',
        'timestamp without time zone': 'timestamp',
        'time with time zone': 'timetz',
        'character': 'char',
        'boolean': 'bool'
      }
      return TYPEMAP[typename] || typename
    },
    columnClass(column) {
      let classes = []
      if(column.is_pk)
        classes.push('pkColumn')
      if(column.is_fk)
        classes.push('fkColumn')
      if(column.is_highlighed)
        classes.push('highlighted')
      return classes.join(' ')
    },
    initGraph() {
      if (typeof cytoscape("core", "nodeHtmlLabel") === "undefined") {
        nodeHtmlLabel(cytoscape);
      }

      this.cy = cytoscape({
        container: this.$refs.cyContainer,
        boxSelectionEnabled: false,
        wheelSensitivity: 0.4,
        style: [
          {
            selector: 'node',
            style: {
              "shape": "round-rectangle",
              "background-color": "#F8FAFC",
              "height": 40,
              "width": 140,
              shape: "round-rectangle",
            }
          },
          {
            selector: 'edge',
            style: {
              'curve-style': 'straight',
              'target-arrow-shape': 'triangle',
              'width': 2,
              'line-style': 'solid'
            }
          },
          {
            selector: 'edge:selected',
            style: {
              'width': 4,
              'line-color': '#1560AD',
              'target-arrow-color': '#1560AD',
              'source-arrow-color': '#1560AD',
            }
          },
        ],
        elements: {
          selectable: true,
          grabbable: false,
          nodes: this.nodes,
          edges: this.edges
        }
      })

      this.cy.on('select unselect', 'edge', function(evt) {
        let should_highlight = evt.type == 'select'
        let {source_col, target_col} = evt.target.data()
        let edge = evt.target
        let srccols = edge.source().data('columns')
        srccols.find((c) => c.name === source_col).is_highlighed = should_highlight
        edge.source().data('columns', srccols)
        let dstcols = edge.target().data('columns')
        dstcols.find((c) => c.name === target_col).is_highlighed = should_highlight
        edge.target().data('columns', dstcols)
      })

      let layout = this.cy.layout({
        name: 'grid',// circle:true, //or breadthfirst
        nodeDimensionsIncludeLabels: true,
        fit: true, // on every layout reposition of nodes, fit the viewport
        padding: 1, // padding around the simulation\
        spacingFactor: 0.8,
      })

      this.cy.on('click', 'node', function (evt) {
        if (evt.originalEvent) {
          const element = document.elementFromPoint(evt.originalEvent.clientX, evt.originalEvent.clientY);
          if(element.dataset.cgid) {
            let edge = this.cy().edges().filter(function( ele ){
              return ele.data('cgid') === element.dataset.cgid;
            })
            setTimeout(function(){edge.select()}, 1)
          }
        }
      })

      this.cy.nodeHtmlLabel(
        [{
          query: 'node', // cytoscape query selector
          cssClass: 'erNode', // any classes will be as attribute of <div> container for every title
          tpl: (function(data) {
            let coldivs = ""
            if (data.columns)
              coldivs = data.columns.map((c) => {
                let dataAttr = ''

                if(c.cgid)
                  dataAttr = `data-cgid="${c.cgid}"`
                  let colName = c.is_fk ? `<a ${dataAttr} href="#" class="colname">${c.name}</a>` : `<span class="colname">${c.name}</span>`
                return `<div ${dataAttr} class="nodeColumn ${this.columnClass(c)}">
                      ${colName}
                  <span class="coltype">${c.type}</span>
                </div>`
              }).join('')

            return `<div id="htmlLabel-${data.id}">
                <div class="nodeTitle">
                  ${data.label}
                </div>
                ${coldivs}
            </div>`;
          }).bind(this)
        }],
      )

      function adjustSizes() {
        const padding = 2;
        this[0].nodes().forEach((node) => {
          let el = $(`#htmlLabel-${node.data().id}`)[0]
          if (el) {
            node.style('width', el.parentElement.clientWidth + padding)
            node.style('height', el.parentElement.clientHeight + padding)
          }
        })
        this[1].run()
        this[2].style.visibility = 'visible'
      }

      // FIXME: do this on render complete instead of just pausing
      setTimeout(adjustSizes.bind([this.cy, layout, this.$refs.cyContainer]), 100)

    },
  },
};
</script>

<style scoped>

</style>