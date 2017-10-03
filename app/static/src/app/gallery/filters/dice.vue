<template>
	<div class="btn-group">
		<button @click="toggleDiceLogic"
			class="btn btn-all" :class="{active: isDiceLogicActive }">{{ diceLogicText }}:</button
		><button @click="toggleDie('basic')"
			class="btn phg-basic-magic" :class="{active: isDieActive('basic') }"
			:disabled="isBasicDisabled" title="Basic"></button
		><button v-for="dieType of diceList" :key="dieType"
			@click="toggleDie(dieType)" :title="capitalize(dieType)"
			class="btn" :class="[isDieActive(dieType) ? 'active' : '', 'phg-' + dieType + '-power']"
			:disabled="!isShowingRelease(dieType)"></button>
	</div>
</template>

<script>
	import {capitalize, includes} from 'lodash'
	import {globals} from 'app/utils'
	
	export default {
		computed: {
			diceList () {
				return globals.diceData
			},
			diceLogicText () {
				return this.$store.state.filters.diceLogic === 'or' ? 'Any' : 'All'
			},
			isDiceLogicActive () {
				return this.$store.state.filters.diceLogic === 'and'
			},
			isBasicDisabled () {
				return this.$store.state.filters.diceLogic === 'and'
			}
		},
		methods: {
			capitalize,
			toggleDiceLogic () {
				this.$store.commit('toggleDiceLogic')
				this.$store.commit('filterCards')
			},
			toggleDie (die) {
				this.$store.commit('toggleDieFilter', die)
				this.$store.commit('filterCards')
			},
			isDieActive (die) {
				return includes(this.$store.state.filters.dice || [], die)
			},
			isShowingRelease (dieType) {
				let releaseNumber = null
				if (dieType === 'divine') {
					releaseNumber = 5
				} else if (dieType === 'sympathy') {
					releaseNumber = 6
				}
				if (!releaseNumber) return true
				return includes(this.$store.state.filters.releases, releaseNumber)
			}
		}
	}
</script>

