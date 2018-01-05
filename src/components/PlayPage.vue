<template>
  <div class="battle-page">
    <div class="players-header">
      <div class="player-panel left">
        <strong v-bind:class="{'active': gameData.turnBy == gameData.myTag}">{{myPlayer.username}}</strong>
        <div class="ships">
          <template v-for="ship in myPlayer.ships">
            <div class="ship" v-bind:class="{'destroyed': ship['destroyed'] == true}">
              <span v-for="cell in getShipSize(ship)"></span>
            </div>
          </template>
        </div>
      </div>
      <div class="player-panel right">
        <strong v-bind:class="{'active': gameData.turnBy != gameData.myTag}">{{enemyPlayer.username}}</strong>
        <div class="ships">
          <template v-for="ship in enemyPlayer.ships">
            <div class="ship" v-bind:class="{'destroyed': ship['destroyed'] == true}">
              <span v-for="cell in getShipSize(ship)"></span>
            </div>
          </template>
        </div>
      </div>
    </div>
    <div class="main-sheet" v-bind:class="{'unactive': gameData.turnBy != gameData.myTag}">
      <template>
        <div class="enemy-sheet">
          <div class="sheet-row" v-for="(row, rI) in enemyPlayer.sheet">
            <div
              class="sheet-item"
              v-bind:class="[calcEnemyItem(rI, cI, item)]"
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
          console.log('cancel mc')
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
        if (item === 'dc') {
          let checkShip = this.checkShip(this.myShips, rI, cI)
          if (checkShip['hp'] <= 0) {
            return 'dsc'
          }
          return item
        }
        let checkShip = this.checkShip(this.myShips, rI, cI)
        if (checkShip) {
          return 'sc'
        }
        let checkBorder = this.checkBorder(this.myPlayer.destroyed_ships, rI, cI)
        if (checkBorder) {
          return 'mc'
        }
        return item
      },
      calcEnemyItem: function (rI, cI, item) {
        let checkShip = this.checkShip(this.enemyPlayer.destroyed_ships, rI, cI)
        if (checkShip) {
          return 'dsc'
        }
        let checkBorder = this.checkBorder(this.enemyPlayer.destroyed_ships, rI, cI)
        if (checkBorder) {
          return 'mc'
        }
        return item
      },
      checkBorder: function (ships, r, c) {
        // Check ship exsisting in getted cell
        // x <= pX + wX
        // x >= pX
        // y <= pY + wY
        // y >= pY
        for (let i = 0; i < ships.length; i++) {
          let ship = ships[i]
          if ((c <= ship.pX + ship.wX) &
            (c >= ship.pX - 1) &
            (r <= ship.pY + ship.wY) &
            (r >= ship.pY - 1)) {
            return ship
          }
        }
        return null
      },
      checkShip: function (ships, r, c) {
        // Check ship exsisting in getted cell
        // x <= pX + wX
        // x >= pX
        // y <= pY + wY
        // y >= pY
        for (let i = 0; i < ships.length; i++) {
          let ship = ships[i]
          if ((c <= ship.pX + ship.wX - 1) &
            (c >= ship.pX) &
            (r <= ship.pY + ship.wY - 1) &
            (r >= ship.pY)) {
            return ship
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
  .main-sheet.unactive {
    opacity: 0.3;
  }
  .my-sheet.mini {
    float: right;
    margin-top: 15px;
  }
</style>
