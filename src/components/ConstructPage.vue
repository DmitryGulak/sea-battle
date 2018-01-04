<template>
  <div class="battle-page">
    <h2 class="big-title">🚢 Place your ships 🚢</h2>
    <!-- Desktop template -->
    <template v-if="device.type != 'mobile'">
      <div class="my-sheet" @mouseup="handleMouseUp" ref="battlePage">
        <div class="sheet-row" v-for="(row, rI) in mySheet">
          <div
            class="sheet-item"
            v-bind:class="[item]"
            v-bind:style="{
              'width': cellWidth + 'px',
              'height': cellWidth + 'px'
            }"
            @click="handleClick(rI, cI)"
            @mouseover="handeMouseOver(rI, cI)"
            @mousedown="handleMouseDown(rI, cI)"
            v-for="(item, cI) in row"></div>
        </div>
      </div>
    </template>
    <!-- Desktop template end -->
    <!-- Mobile template -->
    <template v-else>
      <div class="my-sheet"
           @touchmove="handleTouchMove"
           @touchstart="handleTouchStart"
           @touchend="handleMouseUp">
        <div class="sheet-row" v-for="(row, rI) in mySheet">
          <div
            class="sheet-item"
            v-bind:style="{
              'width': cellWidth + 'px',
              'height': cellWidth + 'px'
            }"
            @click="handleClick(rI, cI)"
            v-bind:class="[item]"
            v-for="(item, cI) in row"></div>
        </div>
      </div>
    </template>
    <!-- Mobile template end -->
    <br>
    <div class="buttons-area">
      <button @click="randomizeShips()" class="btn big">🎲 Random 🎲</button>
      <button  class="btn big success" @click="handleSetupShips()">☑️ Ready ☑️</button>
    </div>
  </div>
</template>

<script>
//  import { mapState } from 'vuex'
  import ClientJS from 'clientjs'
  // EC - Empty Cell
  // SC - Ship cell
  // AC - Active ship cell
  // wX / wY - width in X/Y
  // pX / pY - position by X/Y

  function getRandomInt (min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min
  }

  export default {
    name: 'HelloWorld',
    data () {
      return {
        test: 'check',
        device: false,
        sheetLeft: 8,
        sheetTop: 8,
        sheetWidth: 100,
        cellWidth: 20,
        wX: 10,
        wY: 10,
        border: 1,
        mySheet: [],
        active: null,
        setted: []
      }
    },
    computed: {
      'toSet': {
        get () { return this.$store.state.game.toSet },
        set (value) {
          this.$store.commit('watchGame', { toSet: value })
        }
      }
    },
    methods: {
      handleSetupShips: function () {
        let gameId = this.$route.params['game_id']
        this.$store.commit('watchGame', { myShips: this.setted })
        this.$socket.emit('SETUP_SHIPS', {
          'ships': this.setted,
          'game_id': gameId,
          'user': this.$store.state.user.userData
        })
      },
      handleTouchMove: function (e) {
        let touchCords = this.calcTouchCell(e)
        this.handeMouseOver(touchCords.rI, touchCords.cI)
      },
      handleTouchStart: function (e) {
        let touchCords = this.calcTouchCell(e)
        this.handleMouseDown(touchCords.rI, touchCords.cI)
      },
      handleMouseUp: function () {
        console.log('mouse up')
        this.active = null
        this.updateSheet()
      },
      handeMouseOver: function (rI, cI) {
        console.log('mouse over', rI, cI)
        // Move ship
        if (this.active !== null) {
          console.log('move ship', rI, cI)
          let ship = this.setted[this.active]
          this.moveShip(ship, rI, cI)
        }
      },
      handleClick: function (rI, cI) {
        // Rotate ship on click
        console.log('click', rI, cI)
        let foundShip = this.checkShip(rI, cI)
        this.rotateShip(foundShip)
      },
      handleMouseDown: function (rI, cI) {
        console.log('mouse down', rI, cI)
        let foundShip = this.checkShip(rI, cI)
        if (foundShip) this.active = this.setted.indexOf(foundShip)
        this.updateSheet()
      },
      calcTouchCell: function (e) {
        let touchX = e.touches[0].clientX
        let touchY = e.touches[0].clientY
        let rI = Math.floor((touchY - this.sheetTop) / (this.cellWidth + this.border))
        let cI = Math.floor((touchX - this.sheetLeft) / (this.cellWidth + this.border))
        if (rI < 0) rI = 0
        if (cI < 0) cI = 0
        if (rI > this.wX) rI = 10
        if (cI > this.wY) cI = 10
        return {rI: rI, cI: cI}
      },
      calcItem: function (rI, cI) {
        // Calc cell type on sheet
        let item = 'ec'
        let foundShip = this.checkShip(rI, cI)
        if (foundShip) {
          let shipIndex = this.setted.indexOf(foundShip)
          if (shipIndex === this.active) {
            return 'ac'
          }
          return 'sc'
        }
        return item
      },
      moveShip: function (ship, rI, cI) {
        const canPlace = this.canPlaceHere(ship, rI, cI)
        if (!canPlace) {
          this.updateSheet()
          return
        }
        ship.pX = cI
        ship.pY = rI
        let tmpSetted = this.setted
        tmpSetted[this.active] = ship
        this.setted = tmpSetted
        this.updateSheet()
      },
      rotateShip: function (ship) {
        if (ship) {
          const index = this.setted.indexOf(ship)
          const tmp = ship.wX
          ship.wX = ship.wY
          ship.wY = tmp
          const canPlace = this.canPlaceHere(ship, ship.pY, ship.pX)
          if (!canPlace) {
            ship.wY = ship.wX
            ship.wX = tmp
            this.updateSheet()
            return
          }
          let tmpSetted = this.setted
          tmpSetted[index] = ship
          this.setted = tmpSetted
          this.updateSheet()
        }
      },
      canPlaceHere: function (ship, rI, cI) {
        // Ships collision with borders
        let border = this.border
        // rS - row start
        // rE - row end
        // cS - column start
        // cE - column end
        let rS = rI - border
        let rE = rS + ship.wY + border
        let cS = cI - border
        let cE = cS + ship.wX + border
        for (let r = rS; r <= rE; r++) {
          for (let c = cS; c <= cE; c++) {
            let found = this.checkShip(r, c)
            if (found && found !== ship) {
              return false
            }
          }
        }
        if (rI + ship.wY > this.wY) return false
        if (cI + ship.wX > this.wX) return false
        return true
      },
      checkBorder: function (rI, cI) {
        for (let i = 0; i < this.setted.length; i++) {
          let ship = this.setted[i]
          if ((cI <= (ship.pX - 1) + ship.wX) &
            (cI >= (ship.pX - 1)) &
            (rI <= (ship.pY + 1) + ship.wY) &
            (rI >= (ship.pY + 1))) {
            return true
          }
        }
        return false
      },
      checkShip: function (r, c) {
        // Check ship exsisting in getted cell
        // x <= pX + wX
        // x >= pX
        // y <= pY + wY
        // y >= pY
        for (let i = 0; i < this.setted.length; i++) {
          let ship = this.setted[i]
          if ((c <= ship.pX + ship.wX - 1) &
            (c >= ship.pX) &
            (r <= ship.pY + ship.wY - 1) &
            (r >= ship.pY)) {
            return ship
          }
        }
        return null
      },
      updateSheet: function () {
        // Redraw sheet
        console.log('sheet update')
        let newSheet = []
        for (let r = 0; r < this.wY; r++) {
          let newRow = []
          for (let c = 0; c < this.wX; c++) {
            let newItem = this.calcItem(r, c)
            newRow.push(newItem)
          }
          newSheet.push(newRow)
        }
        this.mySheet = newSheet
      },
      calcSheetSizes: function () {
        // Calc position and cell sizes for touch events
        let battlePage = this.$refs.battlePage
        let pageWidth = battlePage.clientWidth
        let bodyWidth = document.querySelector('body').clientWidth
        console.log(this.sheetLeft, this.sheetTop, pageWidth, bodyWidth)
        this.sheetLeft = battlePage.offsetLeft + ((bodyWidth - pageWidth) / 2)
        this.sheetTop = battlePage.offsetTop
        this.sheetWidth = battlePage.clientWidth - 20
        this.cellWidth = (this.sheetWidth / 10)
      },
      randomizeShips: function () {
        // Place ships randomly
        let self = this
        this.setted = []
        let _toSet = JSON.parse(JSON.stringify(this.toSet))
        for (let i = 0; i < _toSet.length; i++) {
          let ship = _toSet[i]
          while (true) {
            ship.pX = getRandomInt(0, self.wX)
            ship.pY = getRandomInt(0, self.wY)
            let rotate = Math.random() >= 0.5
            if (rotate === true) {
              const tmpWX = ship.wX
              const tmpWY = ship.wY
              ship.wX = tmpWY
              ship.wY = tmpWX
            }
            let canPlace = this.canPlaceHere(ship, ship.pY, ship.pX)
            if (canPlace === true) {
              let newSetted = this.setted
              newSetted.push(ship)
              this.setted = newSetted
              break
            }
          }
        }
        this.updateSheet()
      }
    },
    mounted () {
      this.calcSheetSizes()
      let client = new ClientJS()
      this.device = client.getDevice()
      this.randomizeShips()
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>

</style>
