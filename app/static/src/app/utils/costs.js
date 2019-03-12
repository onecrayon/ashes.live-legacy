import {includes} from 'lodash'
import {globals} from 'app/utils'

function costToDiceType (cost) {
	const splitCosts = cost.split(' / ')
	if (splitCosts.length > 1) {
		let types = []
		for (const splitCost of splitCosts) {
			types.push(splitCost.split(':')[0])
		}
		return types.join(' / ')
	}
	return splitCosts[0].split(':')[0]
}

function costToDiceFace (cost) {
	if (cost === 'basic') {
		return null
	}
	const data = cost.split(':')
	// Default to power face
	if (data.length !== 2) {
		return 'power'
	}
	return data[1]
}

function sortDiceTypes (a, b) {
	const aIsBasic = a === 'basic'
	const bIsBasic = b === 'basic'
	if (!aIsBasic && bIsBasic) return -1
	if (aIsBasic && bIsBasic) return 0
	if (aIsBasic && !bIsBasic) return 1
	const aIsSplit = includes(a, '/')
	const bIsSplit = includes(b, '/')
	if (!aIsSplit && bIsSplit) return -1
	if (aIsSplit && bIsSplit) {
		const aSplit = a.split(' / ')
		const bSplit = b.split(' / ')
		if (costToDiceType(aSplit[0]) === costToDiceType(bSplit[0])) {
			return sortDiceTypes(aSplit[1], bSplit[1])
		}
		return sortDiceTypes(aSplit[0], bSplit[0])
	}
	if (aIsSplit && !bIsSplit) return 1
	const aPos = globals.diceData.indexOf(costToDiceType(a))
	const bPos = globals.diceData.indexOf(costToDiceType(b))
	if (aPos === bPos) {
		const aFace = costToDiceFace(a)
		const bFace = costToDiceFace(b)
		if ((aFace === 'power' && bFace !== 'power') || (aFace === 'class' && !bFace)) {
			return -1
		}
		if (aFace === bFace) return 0
		else return 1
	}
	return aPos < bPos ? -1 : 1
}

function getSortedCostKeys (costObject) {
	let keys = Object.keys(costObject)
	keys.sort(sortDiceTypes)
	return keys
}

function extractDiceRequired (costs, costObject) {
	if (!costObject) {
		return
	}
	for (const key of Object.keys(costObject)) {
		const diceType = costToDiceType(key)
		costs[diceType] = costs[diceType] ? costs[diceType] + costObject[key] : costObject[key]
	}
}

function extractMagicCosts (costs, cards, returnEffectCost) {
	for (const card of cards) {
		const costObject = !returnEffectCost ? card.magicCost : card.effectMagicCost
		if (!costObject) continue
		for (const key of Object.keys(costObject)) {
			costs[key] = costs[key] ? costs[key] + costObject[key] : costObject[key]
		}
	}
}

function getFormattedCosts (costs) {
	let formattedCosts = []
	const keys = getSortedCostKeys(costs)
	for (const key of keys) {
		const dice = key.split(' / ')
		let finalCosts = []
		let firstIteration = true
		for (const cost of dice) {
			if (firstIteration) {
				finalCosts.push([costs[key], ' [[', cost, ']]'].join(''))
				firstIteration = false
			} else {
				finalCosts.push(['[[', cost, ']]'].join(''))
			}
		}
		if (finalCosts.length > 1) {
			formattedCosts.push(finalCosts)
		} else {
			formattedCosts.push(finalCosts[0])
		}
	}
	if (!formattedCosts.length) {
		return null
	}
	return formattedCosts
}

function getPlayCost (costObject) {
	let total = 0
	if (costObject) {
		for (const value of Object.values(costObject)) {
			total += value
		}
	}
	return total
}

export {
	extractDiceRequired,
	extractMagicCosts,
	getFormattedCosts,
	getPlayCost,
	getSortedCostKeys
}
