declare module 'sm-crypto' {
  export const sm2: {
    doEncrypt(data: string, publicKey: string, mode?: number): string;
    doDecrypt(data: string, privateKey: string, mode?: number): string;
  };
}