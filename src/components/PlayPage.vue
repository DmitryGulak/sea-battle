<template>
  <div class="battle-page">
    <div class="players-header">
      <div class="player-panel left">
        <strong v-bind:class="{'active': gameData.turnBy == gameData.myTag}">{{myPlayer.username}}</strong>
        <div class="ships">
          <template v-for="ship in myPlayer.ships">
            <div class="ship" v-bind:class="{'destroyed': ship['hp'] <= 0}">
              <span v-for="cell in getShipSize(ship)"></span>
            </div>
          </template>
        </div>
      </div>
      <div class="player-panel right">
        <strong v-bind:class="{'active': gameData.turnBy != gameData.myTag}">{{enemyPlayer.username}}</strong>
        <div class="ships">
          <template v-for="ship in enemyPlayer.ships">
            <div class="ship" v-bind:class="{'destroyed': ship['hp'] <= 0}">
              <span v-for="cell in getShipSize(ship)"></span>
            </div>
          </template>
        </div>
      </div>
    </div>
    <div class="main-sheet">
      <template>
        <div class="enemy-sheet">
          <div class="sheet-row" v-for="(row, rI) in enemyPlayer.sheet">
            <div
              class="sheet-item"
              v-bind:class="[item]"
              v-bind:style="{
                'width': cellWidth + 'px',
                'height': cellWidth + 'px'
              }"
              @click="handleClick(rI, cI)"
              v-for="(item, cI) in row"></div>
          </div>
        </div>
      </template>
    </div>
    <div class="my-sheet mini">
      <div class="sheet-row" v-for="(row, rI) in myPlayer.sheet">
        <div
          class="sheet-item"
          v-bind:class="[calcItem(rI, cI, item)]"
          v-bind:style="{
            'width': '10px',
            'height': '10px'
          }"
          @click="handleClick(rI, cI)"
          v-for="(item, cI) in row"></div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'playing-page',
    data () {
      return {
        device: false,
        sheetWidth: 100,
        cellWidth: 20,
        wX: 10,
        wY: 10
      }
    },
    computed: {
      'gameData': {
        get () { return this.$store.state.game }
      },
      'myPlayer': {
        get () { return this.$store.state.game.firstPlayer }
      },
      'myShips': {
        get () { return this.$store.state.game.myShips }
      },
      'enemyPlayer': {
        get () {
          return this.$store.state.game.secondPlayer
        }
      }
    },
    methods: {
      handleClick: function (rI, cI) {
        if (['dc', 'mc'].indexOf(this.enemyPlayer['sheet'][rI][cI]) !== -1) {
          return
        }
        let gameId = this.$route.params['game_id']
        this.$socket.emit('PICK_CELL', {
          'rI': rI,
          'cI': cI,
          'game_id': gameId,
          'user': this.$store.state.user.userData
        })
      },
      getShipSize: function (ship) {
        let arr = []
        for (let i = 0; i < ship['wX'] * ship['wY']; i++) {
          arr.push('i')
        }
        return arr
      },
      calcItem: function (rI, cI, item) {
        if (item === 'dc') return item
        if (this.checkShip(rI, cI)) {
          return 'sc'
        }
        return item
      },
      checkShip: function (r, c) {
        // Check ship exsisting in getted cell
        // x <= pX + wX
        // x >= pX
        // y <= pY + wY
        // y >= pY
        for (let i = 0; i < this.myShips.length; i++) {
          let ship = this.myShips[i]
          if ((c <= ship.pX + ship.wX - 1) &
            (c >= ship.pX) &
            (r <= ship.pY + ship.wY - 1) &
            (r >= ship.pY)) {
            return true
          }
        }
        return null
      },
      calcSheetSizes: function () {
        // Calc position and cell sizes for touch events
        let battlePage = this.$parent.$refs.gamePage
        this.sheetWidth = battlePage.clientWidth - 20
        this.cellWidth = (this.sheetWidth / 10)
      }
    },
    mounted () {
      this.calcSheetSizes()
    }
  }
</script>

<style>
  .main-sheet {
    display: block;
    width: 100%;
  }
  .my-sheet.mini {
    float: right;
    margin-top: 15px;
  }
</style>
