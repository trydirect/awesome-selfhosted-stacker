use proc_macro::TokenStream;

#[proc_macro]
pub fn placeholder(_item: TokenStream) -> TokenStream {
    "".parse().unwrap()
}
