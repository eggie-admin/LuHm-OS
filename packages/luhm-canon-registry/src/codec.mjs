/** Pure, bounded UTF-8 identity codec. Hex is representation, never authority. */
const IDENT = /^[a-z][A-Za-z0-9]{0,79}$/;
const SHORTHAND = /^[a-z][a-z0-9]{0,11}$/;
const HEX = /^(?:[0-9a-f]{2})+$/;
const ASCII = /^[\x00-\x7f]*$/;
const encoder = new TextEncoder();
const decoder = new TextDecoder("utf-8", { fatal: true });

export function canonicalName(value) {
  if (typeof value !== "string" || !IDENT.test(value) || !ASCII.test(value)) {
    throw new TypeError("RED_IDENTITY_CAMEL_HUMP");
  }
  return value;
}

export function encodeCanonicalHex(value) {
  canonicalName(value);
  return Array.from(encoder.encode(value),
    (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function decodeCanonicalHex(value) {
  if (typeof value !== "string" || !HEX.test(value)
      || value.length > 160 || value.length % 2 !== 0) {
    throw new TypeError("RED_IDENTITY_HEX_SHAPE");
  }
  const bytes = new Uint8Array(value.length / 2);
  for (let i = 0; i < value.length; i += 2) {
    bytes[i / 2] = Number.parseInt(value.slice(i, i + 2), 16);
  }
  const result = decoder.decode(bytes);
  canonicalName(result);
  if (encodeCanonicalHex(result) !== value) {
    throw new TypeError("RED_IDENTITY_NONCANONICAL_HEX");
  }
  return result;
}

export function assertShorthand(value) {
  if (typeof value !== "string" || !SHORTHAND.test(value)) {
    throw new TypeError("RED_IDENTITY_SHORTHAND");
  }
  return value;
}

export function hexIsReversible(value) {
  return typeof value === "string" && HEX.test(value)
    && value.length <= 160 && value.length % 2 === 0;
}
