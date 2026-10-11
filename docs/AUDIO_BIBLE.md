# Wordline Animation — Audio Bible

## Goal

Audio should make the animation feel alive, funny, cinematic, and intentional.

The current library is useful but too transition-heavy. Wordline needs a broader **storytelling SFX library**, not just whooshes, risers, and bass drops.

## Priority order

Build the library in this order:

1. **Human-scale Foley**
   - footsteps: concrete, office floor, grass, gravel, wood, wet ground
   - sitting / standing / chair movement
   - clothing movement
   - hand contact
   - object pickup / set-down
   - door open / close / latch
   - paper
   - bag / backpack
   - keys
   - phone handling

2. **Object sounds**
   - cup pickup / set-down
   - sip / gulp / swallow
   - bottle
   - glass
   - cans
   - table knocks
   - chair rolls / squeaks
   - computer typing
   - mouse clicks
   - appliance hums
   - vending machine
   - clocks

3. **Comedy impacts**
   - soft thud
   - body fall
   - hard thud
   - tiny bonk
   - cartoon pop
   - rubbery hit
   - sudden stop
   - awkward silence sting
   - tiny success ding
   - anticlimax hit

4. **Movement**
   - subtle cloth whoosh
   - fast body pass
   - jump
   - launch
   - fall
   - slide
   - skid
   - spin
   - object flyby

5. **Environment / ambience**
   - quiet office
   - busy office
   - apartment
   - city day
   - city night
   - park
   - café
   - restaurant
   - school hallway
   - beach
   - harbor
   - rain
   - wind
   - crowd walla

6. **Disaster / spectacle**
   - distant rumble
   - debris
   - concrete crack
   - structural groan
   - glass break
   - heavy impact
   - water surge
   - wave crash
   - tsunami roar
   - vehicle reactions
   - alarms and sirens

7. **Small character reactions**
   - gasp
   - sigh
   - laugh
   - confused murmur
   - panic breath
   - crowd surprise
   - restrained reactions rather than meme screams

## Sound-design rule

Do not plaster an effect onto every movement.

Use three layers:
- **world layer:** ambience and room tone
- **physical layer:** Foley and impacts
- **comedy / story layer:** only the sounds that sell the beat or punchline

Silence is part of the design.

## Running-joke audio signatures

Recurring jokes should develop stable audio identities.

### The 4:17 Guy
**THUD → SIP → FWOOOP**

Keep those three beats recognizable between appearances.

### Unnecessary Tsunami
Do not turn it into a generic meme explosion.

The funniest version is usually:
- wholesome / ordinary music continues
- minimal warning
- huge visual reveal
- restrained distant water / air sound if needed
- hard cut before or at impact

The contrast is the joke.

## Music system

Wordline does not need one permanent musical genre.

Use music by story function:

- **Wholesome:** warm acoustic, light piano, gentle strings
- **Comedy:** quirky percussion, pizzicato, playful bass, light funk
- **Curiosity / What-if:** bright pulsing synth, marimba, light cinematic rhythm
- **Adventure:** energetic orchestral / hybrid percussion
- **Tension:** restrained pulse, low percussion, sparse texture
- **Absurd escalation:** music that stays emotionally sincere while visuals become ridiculous
- **Payoff:** bigger version of the same musical idea rather than an unrelated trailer cue

Avoid overly epic trailer music for ordinary jokes unless the mismatch itself is the joke.

## YouTube-first sourcing policy

Preferred order:

1. **YouTube Audio Library** for music and many general SFX
2. **Mixkit** for free SFX and selected music
3. **Pixabay** for gaps, while recording the source/license and avoiding Content-ID-marked music where practical
4. **Freesound CC0** for niche Foley and unusual sounds

For Freesound, default to CC0. Use CC-BY only when the sound is worth the attribution work. Avoid CC-BY-NC for anything that may be monetized.

## Library structure

```
SFX/
  ambience/
    office/
    city/
    nature/
    interiors/
  foley/
    footsteps/
    cloth/
    doors/
    chairs/
    hands/
    objects/
  props/
    cups/
    phones/
    computers/
    kitchen/
    vehicles/
  comedy/
    bonks/
    pops/
    anticlimax/
    stings/
  movement/
    whooshes/
    falls/
    launches/
    slides/
  impacts/
    soft/
    hard/
    body/
    debris/
  disaster/
    water/
    destruction/
    weather/
    alarms/
  reactions/
    human/
    crowds/
  music/
    wholesome/
    comedy/
    curiosity/
    adventure/
    tension/
    absurd/
  manifests/
```

Every externally sourced file should eventually have metadata with:
- original filename
- source
- creator when applicable
- license
- source page
- date downloaded
- attribution requirement
- Content ID warning when applicable

## Mixing target

For YouTube:
- dialogue/narration always wins
- ambience quiet and continuous
- Foley readable but not exaggerated by default
- comedy impacts can briefly jump forward
- music should support rather than smother the animation
- preserve headroom; avoid constant limiter-pumping
- target roughly -14 LUFS integrated for finished videos, with true peak at or below about -1 dBTP unless a specific delivery test says otherwise

The objective is not "more sound."

The objective is **better-timed sound**.
