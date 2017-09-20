<template>
	<div class="filters">
		<div class="btn-group">
			<button v-on:click="toggleDiceLogic"
				class="btn btn-all" :class="{active: isDiceLogicActive }">{{ diceLogicText }}:</button
			><button v-on:click="toggleDie('basic')"
				class="btn phg-basic-magic" :class="{active: isDieActive('basic') }"
				:disabled="isBasicDisabled" title="Basic"></button
			><button v-on:click="toggleDie('ceremonial')"
				class="btn phg-ceremonial-power" :class="{active: isDieActive('ceremonial') }"
				title="Ceremonial"></button
			><button v-on:click="toggleDie('charm')"
				class="btn phg-charm-power" :class="{active: isDieActive('charm') }"
				title="Charm"></button
			><button v-on:click="toggleDie('illusion')"
				class="btn phg-illusion-power" :class="{active: isDieActive('illusion') }"
				title="Illusion"></button
			><button v-on:click="toggleDie('natural')"
				class="btn phg-natural-power" :class="{active: isDieActive('natural') }"
				title="Natural"></button
			><button v-on:click="toggleDie('divine')"
				class="btn phg-divine-power" :class="{active: isDieActive('divine') }"
				:disabled="isSetDisabled(5)" title="Divine">D</button
			><button v-on:click="toggleDie('sympathy')"
				class="btn phg-sympathy-power" :class="{active: isDieActive('sympathy') }"
				:disabled="isSetDisabled(6)" title="Sympathy">S</button>
		</div>
		<div class="btn-group">
			<button v-on:click="toggleCardType('Ally')"
				class="btn btn-small" :class="{active: isTypeActive('Ally')}">Ally</button
			><button v-on:click="toggleCardType('Action Spell')"
				class="btn btn-small" :class="{active: isTypeActive('Action Spell')}">Action</button
			><button v-on:click="toggleCardType('Reaction Spell')"
				class="btn btn-small" :class="{active: isTypeActive('Reaction Spell')}">Reaction</button
			><button v-on:click="toggleCardType('Alteration Spell')"
				class="btn btn-small" :class="{active: isTypeActive('Alteration Spell')}">Alteration</button
			><button v-on:click="toggleCardType('Ready Spell')"
				class="btn btn-small" :class="{active: isTypeActive('Ready Spell')}">Ready</button
			><button v-on:click="toggleCardType('summon')"
				class="btn btn-small" :class="{active: isTypeActive('summon')}">Summon</button
			>
		</div>
		<div class="btn-group">
			<button v-on:click="toggleOrdering()"
				class="btn btn-small">Sort <i class="fa" :class="orderIconClass"></i></button
			><button v-on:click="sortBy('name')"
				class="btn btn-small" :class="{active: isSortedBy('name')}">Name</button
			><button v-on:click="sortBy('type')"
				class="btn btn-small" :class="{active: isSortedBy('type')}">Type</button
			><!--<button v-on:click="sortBy('dice')"
				class="btn btn-small" :class="{active: isSortedBy('dice')}">Dice</button
			>--><button v-on:click="sortBy('weight')"
				class="btn btn-small" :class="{active: isSortedBy('weight')}">Cost</button
			>
		</div>
	</div>
</template>

<script>
	import {includes} from 'lodash'

	export default {
		computed: {
			diceLogicText () {
				return this.$store.state.filters.diceLogic == 'or' ? 'Any' : 'All'
			},
			isDiceLogicActive () {
				return this.$store.state.filters.diceLogic == 'and'
			},
			isBasicDisabled () {
				return this.$store.state.filters.diceLogic == 'and'
			},
			orderIconClass () {
				return 'fa-sort-' + (this.$store.state.filters.primaryOrder == 1 ? 'asc' : 'desc')
			}
		},
		methods: {
			toggleDiceLogic () {
				this.$store.commit('toggleDiceLogic')
				this.$store.commit('filterCards')
			},
			toggleDie (die) {
				this.$store.commit('toggleDieFilter', die)
				this.$store.commit('filterCards')
			},
			toggleCardType (typeName) {
				this.$store.commit('toggleTypeFilter', typeName)
				this.$store.commit('filterCards')
			},
			toggleOrdering () {
				this.$store.commit('toggleSortOrder')
				this.$store.commit('filterCards')
			},
			sortBy (field) {
				this.$store.commit('setSort', field)
				this.$store.commit('filterCards')
			},
			isDieActive (die) {
				return includes(this.$store.state.filters.dice || [], die)
			},
			isTypeActive (typeName) {
				return includes(this.$store.state.filters.types || [], typeName)
			},
			isSetDisabled (setNumber) {
				return !includes(this.$store.state.filters.releases, setNumber)
			},
			isSortedBy (field) {
				return this.$store.state.filters.primarySort == field
			}
		}
	}
</script>
